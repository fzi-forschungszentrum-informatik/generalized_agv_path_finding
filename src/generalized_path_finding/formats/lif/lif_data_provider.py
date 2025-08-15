import json
import math
import warnings
from enum import Enum
from pathlib import Path
from typing import Callable

import networkx as nx
from auto_all import public

from generalized_path_finding.model.data_provider import NetworkxDataProvider
from generalized_path_finding.model.networkx_data import NetworkxData
from .edge import Edge
from .lif import LIF
from .node import NodePosition, Node


@public
class DistanceType(str, Enum):
    """
    What kind of distance to use for a graph when extracting it from a LIF object.
    """

    Euclidean = 'Euclidean'
    """
    Use the distance in the Euclidean plane for distance measurements.
    
    See :func:`euclidean_distance`
    """
    Manhattan = 'Manhattan'
    """
    Use the sum of the differences in each coordinate for distance measurements.
    
    See :func:`manhattan_distance`
    """
    TrajectoryOrEuclidean = 'TrajectoryOrEuclidean'
    """
    Use the trajectory given for the edge in the LIF file for distance measurements.
    
    If there is no trajectory given for an edge, the Euclidean distance is used instead.
    
    Note: The the Euclidean distance is a lower bound to trajectory length and can thus be used as an heuristic.
    """


def euclidean_distance(a: NodePosition, b: NodePosition) -> float:
    """
    Calculate the Euclidean distance between two NodePositions, as in ``sqrt((a.x - b.x)^2 + (a.y - b.y)^2)``.

    :param a: the first NodePosition
    :param b: the second NodePosition
    :return: Euclidean distance
    """
    return math.hypot(a.x - b.x, a.y - b.y)


def manhattan_distance(a: NodePosition, b: NodePosition) -> float:
    """
    Calculate the Manhattan distance between two NodePositions, as in ``|a.x - b.x| + |a.y - b.y|``.

    :param a: first NodePosition
    :param b: second NodePosition
    :return: Manhattan distance
    """
    return abs(a.x - b.x) + abs(a.y - b.y)


def _edge_cost(edge: Edge, vehicle_type_id, distance_type, nodes, time_cost, vehicle_max_speed):
    edge_props = edge.get_properties_for_vehicle_type(vehicle_type_id)
    if edge_props is None \
            or nodes[edge.start_node_id].get_properties_for_vehicle_type(vehicle_type_id) is None \
            or nodes[edge.end_node_id].get_properties_for_vehicle_type(vehicle_type_id) is None:
        return None  # meaning this edge should not be put in the graph

    match distance_type:
        case DistanceType.Euclidean:
            cost = euclidean_distance(
                nodes[edge.start_node_id].node_position,
                nodes[edge.end_node_id].node_position
            )
        case DistanceType.Manhattan:
            cost = manhattan_distance(
                nodes[edge.start_node_id].node_position,
                nodes[edge.end_node_id].node_position
            )
        case DistanceType.TrajectoryOrEuclidean:
            if edge_props.trajectory is not None:
                cost = edge_props.trajectory.approximate_length()
            else:
                cost = euclidean_distance(
                    nodes[edge.start_node_id].node_position,
                    nodes[edge.end_node_id].node_position
                )

    if time_cost:
        if vehicle_max_speed == float('inf') and edge_props.max_speed is None:
            raise ValueError(f"Using time cost, but there is no speed limit on edge {edge.edge_id}. Use "
                             f"vehicle_max_speed parameter or explicitly specify infinite maxSpeed in LIF file.")
        speed = min(edge_props.max_speed, vehicle_max_speed) if edge_props.max_speed is not None else vehicle_max_speed
        cost /= speed

    return cost


def _lif_to_graph(
        lif: LIF,
        vehicle_type_id: str,
        distance_type: DistanceType,
        time_cost: bool = False,
        vehicle_max_speed: float = float("infinity"),
) -> nx.MultiDiGraph:
    """
    Convert a LIF object to a NetworkX Graph.
    """

    # nodes are created regardless of vehicle_type, but edges using filtered out nodes will not be added
    nodes: dict[str, Node] = {}
    for layout in lif.layouts:
        for node in layout.nodes:
            nodes[node.node_id] = node

    # It would be a bad idea to support stations as graph nodes, query source or target, because they might make
    # paths traversing stations seem shorter than they are.
    # Example: A--5--[B--1--C]--5--D    (A-D are nodes, numbers are edges weights, B and C form the station S together)
    # query(A, S) == 5 and query(S, D) == 5 makes us think that query(A, D) <= 10 whereas query(A, D) == 11 is the case

    edges = []
    for layout in lif.layouts:
        for edge in layout.edges:
            cost = _edge_cost(edge, vehicle_type_id, distance_type, nodes, time_cost, vehicle_max_speed)
            if cost is not None:
                edges.append((edge.start_node_id, edge.end_node_id, edge.edge_id, {"lif_edge": edge, "weight": cost}))

    if len(edges) == 0:
        warnings.warn(f"Generating empty graph because no edges are supporting vehicle type {vehicle_type_id}")

    graph = nx.MultiDiGraph(edges)
    for node_id, node in nodes.items():
        graph.add_node(node_id, lif_node=node)

    return graph


@public
class LifDataProvider(NetworkxDataProvider[str]):
    """
    Extracts data from a LIF (Layout Interchange Format) file.

    All layouts are converted. All nodes and edges are converted.
    All node and edge properties are put into the graph.
    This ignores stations, actions, orientation of nodes and restrictions on rotation on edges or on nodes.
    """

    def __init__(
            self,
            path: str | Path,
            distance_type: DistanceType = DistanceType.Euclidean,
            vehicle_type_id: str = None,  # use only one if none is given (check if there is only one)
            time_cost: bool = False,
            vehicle_max_speed: float = float("infinity"),
    ):
        """
        A DataProvider fed by a LIF file on disk.

        :param path: path to the LIF file
        :param distance_type: the DistanceType to use as cost of arcs
        :param vehicle_type_id: the vehicle type ID from whose view to look at the layout,
            can be omitted if all edges only name the same, single vehicle type ID.
        :param time_cost: whether to use time instead of distance as cost
        :param vehicle_max_speed: the maximum speed of the vehicle (only relevant if time_cost is ``True``)
        """

        self.path = path

        self.vehicle_type_id = vehicle_type_id
        self.distance_type = distance_type
        self.time_cost = time_cost
        self.vehicle_max_speed = vehicle_max_speed

        # not checking infinite speed limit here, because it's checked more granularly in _edge_cost

        # lazy properties
        self._lif = None
        self._graph = None
        self._heuristic = None

    def get_networkx_data(self) -> NetworkxData[str]:
        return NetworkxData(self._get_graph(), self._get_heuristic())

    def _get_graph(self) -> nx.MultiDiGraph:
        if self._graph is not None: return self._graph

        with open(self.path) as file:
            self._lif = LIF.from_camel_dict(json.load(file))

        self._impute_vehicle_type_id()
        self._graph = _lif_to_graph(self._lif, self.vehicle_type_id, self.distance_type, self.time_cost,
                                    self.vehicle_max_speed)
        return self._graph

    def _impute_vehicle_type_id(self):
        """
        Test if there is exactly one vehicle type ID allowed on the edge and if yes return it.
        Otherwise, raise an exception.

        :return: The only vehicle type ID.
        """

        if self.vehicle_type_id is None:
            vehicle_type_ids = set(props.vehicle_type_id
                                   for layout in self._lif.layouts
                                   for edge in layout.edges
                                   for props in edge.vehicle_type_edge_properties)
            if len(vehicle_type_ids) == 1:
                self.vehicle_type_id = vehicle_type_ids.pop()
            else:
                raise RuntimeError("There is more than one vehicle type in the LIF file. Specify the vehicle type "
                                   "using `LifDataProvider(vehicle_type_id=...)`")

    def _get_heuristic(self) -> Callable[[str, str], float]:
        if self._heuristic is not None: return self._heuristic
        self._get_graph()

        if self.distance_type == DistanceType.Euclidean or self.distance_type == DistanceType.TrajectoryOrEuclidean:
            def heuristic(a: str, b: str) -> float:
                return euclidean_distance(
                    self._graph.nodes[a]["lif_node"].node_position,
                    self._graph.nodes[b]["lif_node"].node_position
                ) / (self.vehicle_max_speed if self.time_cost else 1.0)

            self._heuristic = heuristic
        else:  # if self.distance_type == DistanceType.Manhattan:
            def heuristic(a: str, b: str) -> float:
                return manhattan_distance(
                    self._graph.nodes[a]["lif_node"].node_position,
                    self._graph.nodes[b]["lif_node"].node_position
                ) / (self.vehicle_max_speed if self.time_cost else 1.0)

            self._heuristic = heuristic

        # other cases are impossible, because get_graph will through before coming here

        return self._heuristic
