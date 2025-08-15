import os
import pathlib
from enum import Enum

import geopandas
import networkx as nx
import pandas as pd
from pyrosm import OSM
from pyroutingkit import GraphPreparator, RoutingMode

from generalized_path_finding.formats.osm.routing_kit_filters import OSMWayDirectionCategory, is_osm_way_used_by_cars, \
    is_osm_way_used_by_bicycles, is_osm_way_used_by_pedestrians, get_osm_way_speed, get_osm_car_direction_category, \
    get_osm_bicycle_direction_category
from generalized_path_finding.model import NetworkxDataProvider, NetworkxData
from generalized_path_finding.model.data_provider import OsmChDataProvider
from generalized_path_finding.model.osm_ch_data import OsmChData
from generalized_path_finding.nodes import GeoCoords

KPH_PER_MPS = 3.6


def is_file_more_recent(test_file, reference_file) -> bool:
    assert os.path.isfile(reference_file)
    return os.path.isfile(test_file) and os.path.getmtime(test_file) > os.path.getmtime(reference_file)


class TransportMode(Enum):
    CAR = 0
    BIKE = 1
    PEDESTRIAN = 2

    def to_routing_kit(self) -> RoutingMode:
        match self:
            case TransportMode.CAR:
                return RoutingMode.CAR
            case TransportMode.BIKE:
                return RoutingMode.BIKE
            case TransportMode.PEDESTRIAN:
                return RoutingMode.PEDESTRIAN
        raise ValueError(f"Unknown transport mode: {self}")

    def to_pyrosm(self) -> str:
        match self:
            case TransportMode.CAR:
                return "driving"
            case TransportMode.BIKE:
                return "cycling"
            case TransportMode.PEDESTRIAN:
                return "walking"
        raise ValueError(f"Unknown transport mode: {self}")


class OsmDataProvider(OsmChDataProvider, NetworkxDataProvider):

    def __init__(
            self,
            pbf_file: str | pathlib.Path,
            transport_mode: TransportMode = TransportMode.CAR,
            time_cost: bool = True,
            max_speed: float = None
    ):
        """
        A DataProvider to prepare and provide OSM data in the Contraction Hierarchy and .graph file format from a
        .pbf extract from OpenStreetMap.

        :param pbf_file: the path of the .pbf file to use as input. The .graph and .ch files will be created in the
        same directory and with the same name, but with different extensions. If they already exist, they will be
        used, provided that they are more recent than the .pbf file.
        :param transport_mode: the transport mode to use for routing. Defaults to car routing.
        :param time_cost: whether to use time instead of distance as cost. Defaults to True. RoutingKit only supports time cost.
        :param max_speed: the maximum speed of the transport mode in meters per second.
        For cars, the max speed on each arc is always assumed. For bikes the default is 15 km/h. For pedestrians the
        default is 4 km/h. The bike and pedestrian speeds can be overridden by specifying a different value.
        """

        self.pbf_file = str(pbf_file)
        self.transport_mode = transport_mode
        self.time_cost = time_cost
        if max_speed is not None:
            self.max_speed = max_speed
        else:
            match transport_mode:
                case TransportMode.CAR:
                    self.max_speed = 130 / KPH_PER_MPS  # never used
                case TransportMode.BIKE:
                    self.max_speed = 15 / KPH_PER_MPS
                case TransportMode.PEDESTRIAN:
                    self.max_speed = 4 / KPH_PER_MPS

        self._graph_file = None
        self._ch_file = None
        self._graph = None
        self._heuristic = None

    def get_osm_ch_data(self) -> OsmChData:
        if not self.time_cost:
            raise ValueError("OsmChData is only compatible with time cost. Set time_cost=True in OsmDataProvider.")
            # FEATURE: see OsmRoutingKit

        if self._graph_file is None or self._ch_file is None:
            self._prepare_osm(self.pbf_file)

        return OsmChData(self._graph_file, self._ch_file)

    def _prepare_osm(self, pbf_file: str):
        if self.transport_mode != TransportMode.CAR:
            speed_spec = f"_{self.max_speed}mps"
        else:
            speed_spec = ""
        spec = f"{self.transport_mode.name}{speed_spec}"
        self._graph_file = f"{pbf_file}_{spec}.graph"
        self._ch_file = f"{pbf_file}_{spec}.ch"

        if is_file_more_recent(self._graph_file, self.pbf_file) and is_file_more_recent(self._ch_file,
                                                                                        self._graph_file):
            print(".graph and .ch already up-to-date")
        else:
            print("converting .pbf to .graph and .ch")
            preparator = GraphPreparator(self.pbf_file)
            preparator.prepareGraph(self._graph_file, self._ch_file, self.transport_mode.to_routing_kit(),
                                    round(self.max_speed * 3.6), round(self.max_speed * 3.6))

    def get_networkx_data(self) -> NetworkxData[GeoCoords]:
        if self._graph is None or self._heuristic is None:
            self._prepare_nx_data()

        return NetworkxData(self._graph, self._heuristic)

    def _graph_from_osm(self, osm: OSM):
        # This attempts to totally mimic the behavior of RoutingKit's load_osm_routing_graph_from_pbf
        # https://github.com/RoutingKit/RoutingKit/blob/6e897bcf47e24ec6cf7294e9cf826adf8e055e7c/src/osm_graph_builder.cpp#L116
        # Turn restrictions are missing, though.

        # Edge filtering seems to almost work. For Andorra, I have 97321 edges (forward + backward), while
        # RoutingKit has 94026 edges (forward + backward, modelling nodes are routing nodes).

        nodes, edges = osm.get_network(nodes=True, network_type="all")
        way_filter = {
            TransportMode.CAR: is_osm_way_used_by_cars,
            TransportMode.BIKE: is_osm_way_used_by_bicycles,
            TransportMode.PEDESTRIAN: is_osm_way_used_by_pedestrians,
        }[self.transport_mode]
        edges = edges[edges.apply(way_filter, axis=1)]

        direction_getter = {
            TransportMode.CAR: get_osm_car_direction_category,
            TransportMode.BIKE: get_osm_bicycle_direction_category,
            TransportMode.PEDESTRIAN: lambda _id, _tags: OSMWayDirectionCategory.OPEN_IN_BOTH
        }[self.transport_mode]

        if self.transport_mode in [TransportMode.CAR, TransportMode.BIKE]:
            directed_edges = []
            no_edges = []

            for idx, row in edges.iterrows():
                direction = direction_getter(row.id, row)

                match direction:
                    case OSMWayDirectionCategory.CLOSED:
                        no_edges.append((row.u, row.v, row.id))
                        no_edges.append((row.v, row.u, row.id))
                    case OSMWayDirectionCategory.ONLY_OPEN_FORWARDS:
                        directed_edges.append({**row})
                        no_edges.append((row.v, row.u, row.id))
                    case OSMWayDirectionCategory.ONLY_OPEN_BACKWARDS:
                        no_edges.append((row.u, row.v, row.id))
                        directed_edges.append({**row, 'u': row.v, 'v': row.u})
                    case OSMWayDirectionCategory.OPEN_IN_BOTH:
                        directed_edges.append({**row})
                        directed_edges.append({**row, 'u': row.v, 'v': row.u})

            edges = pd.concat([edges[0:0], geopandas.GeoDataFrame(directed_edges)])

        # OSM.to_graph seems to have a bug: it ignores the direction and treats all edges as bidirectional contrary to
        # documentation. (Though I cannot find the bug in their source code either.)
        # As a workaround, I remove the wrong-direction edges after conversion.

        # debug output:
        # edges_before = [(row.id, row.u, row.v, row.oneway) for idx, row in edges.iterrows() if row.id == 25769024]
        # print(f"edges before ({len(edges_before)}) =")
        # for e in edges_before: print(e)

        graph = OSM.to_graph(nodes, edges, graph_type="networkx")

        # debug output:
        # edges2 = [(d["osmid"], u, v, d["oneway"]) for u, v, d in graph.edges(data=True) if d["osmid"] == 25769024]
        # print(f"edges in between ({len(edges2)}) = ")
        # for e in edges2: print(e)

        if self.transport_mode == TransportMode.CAR:
            for u, v, osm_way_id in no_edges:
                u_v_edges = graph.get_edge_data(u, v)
                if u_v_edges is None: continue
                key = next(key for key, data in u_v_edges.items() if data["osmid"] == osm_way_id)
                graph.remove_edge(u, v, key)

        # debug output:
        # edges3 = [(d["osmid"], u, v, d["oneway"]) for u, v, d in graph.edges(data=True) if d["osmid"] == 25769024]
        # print(f"edges after ({len(edges3)}) = ")
        # for e in edges3: print(e)

        return graph

    def _prepare_nx_data(self):
        osm = OSM(self.pbf_file)
        # FEATURE: Flamegraph to see how slow this is
        graph = self._graph_from_osm(osm)
        # y = latitude, x = longitude

        # convert graph such that GeoCoords are node keys instead of osm node ids
        new_graph = nx.MultiDiGraph()
        node_mapping = {}

        for node_id, data in graph.nodes(data=True):
            coords = GeoCoords(data['y'], data['x'])  # y=lat, x=lon
            node_mapping[node_id] = coords
            new_graph.add_node(coords, osm_id=node_id, **data)

        for u, v, key, data in graph.edges(data=True, keys=True):
            data["osm_id"] = data["key"]
            new_graph.add_edge(node_mapping[u], node_mapping[v], **data)

        graph = new_graph

        # add weights to graph
        for e in graph.edges:
            edge = graph.edges[e]
            edge["weight"] = edge["length"]
            if self.time_cost:
                # FEATURE: impute speed limit based on "highway" attribute (see RoutingKit comment "getting speed")
                speed = get_osm_way_speed(edge["osm_id"], edge) / 3.6  # in m/s
                if self.max_speed is None and speed == float("inf"):
                    raise ValueError(f"Using time cost, but there is no speed limit on edge {e}. Use "
                                     f"vehicle_max_speed parameter or explicitly specify infinite maxSpeed in LIF file.")
                edge["weight"] /= speed

        def heuristic(a: GeoCoords, b: GeoCoords) -> float:
            return a.distance_to(b) / (self.max_speed if self.time_cost else 1.0)

        self._graph = graph
        self._heuristic = heuristic
