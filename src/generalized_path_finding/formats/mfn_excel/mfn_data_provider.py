import math
import pathlib
import warnings
from typing import Callable

import networkx as nx

from generalized_path_finding.model.data_provider import NetworkxDataProvider
from generalized_path_finding.model.networkx_data import NetworkxData
from .connection import Connection
from .mfn import MFN
from .path import Path


def fallback(a, b):
    return a if a is not None else b


def euclidean_distance(a, b) -> float:
    return math.hypot(a.x_meter - b.x_meter, a.y_meter - b.y_meter)


def _mfn_to_graph(
        mfn: MFN,
        fleet_id: str,
        time_cost: bool = False,
        fleet_max_speed: float = float("infinity"),
        priority_factor: Callable[[int], float] = lambda prio: 1,
) -> nx.MultiDiGraph:
    nodes = {node.name: node for node in mfn.nodes}

    def path_cost(path: Path) -> float:
        dist = euclidean_distance(nodes[path.origin_node_name], nodes[path.destination_node_name])
        if time_cost:
            if fleet_max_speed == float("infinity") and path.speed_limit_mps is None:
                raise ValueError(f"Using time cost, but there is no speed limit on path {path.name}. Use "
                                 f"fleet_max_speed parameter or explicitly specify infinite speed_limit in MFN file.")
            speed = (min(path.speed_limit_mps, fleet_max_speed)
                     if path.speed_limit_mps is not None else fleet_max_speed)
            return dist / speed * priority_factor(path.prio)
        else:
            return dist * priority_factor(path.prio)

    def connection_cost(con: Connection) -> float:
        dist = euclidean_distance(nodes[con.origin_node_name], nodes[con.destination_node_name])
        if time_cost:
            return fallback(float(con.cal_trans_duration_seconds), dist / fleet_max_speed)
        else:
            return dist  # this is 0 most of the time, because elevators are vertical

    edges = [
                (path.origin_node_name, path.destination_node_name, path.name, {
                    "mfn_edge": path,
                    "weight": path_cost(path)
                }) for path in mfn.paths if path.supports_fleet(fleet_id)
            ] + [
                (con.origin_node_name, con.destination_node_name, con.name, {
                    "mfn_connection": con,
                    "weight": connection_cost(con)
                }) for con in mfn.connections if con.supports_fleet(fleet_id)
            ]

    if len(edges) == 0:
        warnings.warn(f"Generating empty graph because no paths or connections are supporting fleet {fleet_id}")

    graph = nx.MultiDiGraph(edges)
    for node_id, node in nodes.items():
        graph.add_node(node_id, mfn_node=node)

    return graph


class MfnDataProvider(NetworkxDataProvider[str]):
    """
    Extracts data from an MFN (Multi Floor Network) Excel file (file ending .xlsx).

    All nodes, paths (intra-floor edges) and connections (inter-floor edges) are converted.
    This ignores all values only meant for visualization, as well as descriptions and comments.
    To identify nodes, names are used, not indices (origin_id, dest_id).

    Weights are given in meters or seconds and assume Euclidean distance between nodes.
    """

    def __init__(
            self,
            path: str | pathlib.Path,
            fleet: str = None,
            time_cost: bool = False,
            fleet_max_speed: float = float("infinity"),
            priority_factor: Callable[[int | None], float] = lambda prio: 1,
    ):
        """
        A DataProvider fed by an MFN Excel file on disk.

        :param path: path to the MFN Excel file
        :param fleet: the fleet type name from whose view to look at the layout,
            can be omitted if all paths and connections only name the same set of fleets.
        :param time_cost: whether to use time instead of distance as cost
        :param fleet_max_speed: the maximum speed of vehicles of the given fleet
            (only relevant if time_cost is ``True``)
        :param priority_factor: function taking a priority and returning a value by which to scale the cost of a path
            that has that priority. Because prio is an optional field, this function must also map None.
            Defaults to `lambda prio: 1`, ignoring priority.
        """
        self.path = path

        self.fleet = fleet
        self.time_cost = time_cost
        self.vehicle_max_speed = fleet_max_speed
        self.priority_factor = priority_factor

        # not checking infinite speed limit here, because it's checked more granularly in _mfn_to_graph._path_cost

        # lazy properties
        self._mfn = None
        self._graph = None
        self._heuristic = None
        self._min_priority_factor = None

    def get_networkx_data(self) -> NetworkxData[str]:
        return NetworkxData(self._get_graph(), self._get_heuristic())

    def _get_graph(self) -> nx.MultiDiGraph:
        if self._graph is not None: return self._graph

        self._mfn = MFN(self.path)

        self._impute_fleet()
        self._graph = _mfn_to_graph(self._mfn, self.fleet, self.time_cost,
                                    self.vehicle_max_speed, self.priority_factor)

        # can handle prio=None as well
        self._min_priority_factor = min(self.priority_factor(path.prio) for path in self._mfn.paths)
        return self._graph

    def _impute_fleet(self):
        """
        Test if all paths and connections can be travers by the same set of fleets.
        If so, choose one of them and view the network from its perspective.
        Otherwise, raise an exception.

        :return: One of the fleets, that can travel everywhere.
        """

        if self.fleet is None:
            vehicle_type_ids = (
                    set(frozenset(path.fleet_list) for path in self._mfn.paths) |
                    set(frozenset(con.fleet_list) for con in self._mfn.connections)
            )

            if len(vehicle_type_ids) == 1:
                self.fleet = next(iter((vehicle_type_ids.pop())))
            else:
                raise RuntimeError("There is more than one fleet-list in the MFN Excel file. Specify the vehicle "
                                   "type using `MfnDataProvider(vehicle_type_id=...)`")

    def _get_heuristic(self) -> Callable[[str, str], float]:
        if self._heuristic is not None: return self._heuristic
        self._get_graph()

        def heuristic(a: str, b: str) -> float:
            return euclidean_distance(
                self._graph.nodes[a]["mfn_node"],
                self._graph.nodes[b]["mfn_node"]
            ) / (self.vehicle_max_speed if self.time_cost else 1.0) * self._min_priority_factor

        self._heuristic = heuristic
        return self._heuristic
