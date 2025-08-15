from dataclasses import dataclass

from auto_all import public
from pyroutingkit import PointLatLon, RoutingService, Route, RouteArc

from generalized_path_finding.model.osm_ch_data import OsmChData
from generalized_path_finding.model.path import Path
from generalized_path_finding.model.pathfinder import PathFinder
from generalized_path_finding.nodes import GeoCoords

"""
RoutingKit uses these units:
- distance: meters
- latitude: degrees in [-90, +90]  
- longitude: degrees in in [-180, +180]

Reference:
https://github.com/RoutingKit/RoutingKit/blob/fc0ee9dcce601ba1f98a3c4155740cef6f2e92c3/include/routingkit/geo_dist.h#L8
"""

MATCHING_RADIUS = 100
"""The radius in meters within which a node is considered to be matching a PointLatLon."""


def geo_location_to_point_lat_lon(geo_location: GeoCoords) -> PointLatLon:
    return PointLatLon(geo_location.lat, geo_location.lon)


def point_lat_lon_to_geo_location(point_lat_lon: PointLatLon) -> GeoCoords:
    return GeoCoords(point_lat_lon.latitude, point_lat_lon.longitude)


@public
@dataclass
class OsmArc:
    """
    An Arc groups several OSM nodes within an OSM way that have no routing decision but are purely for geometry.
    This class provides attributes of such an arc.
    """
    # because RouteArc is not properly typed by pybind11

    osmWayId: int
    startOsmNodeId: int
    endOsmNodeId: int

    geometry: list[GeoCoords]

    distance: float
    duration: float

    @staticmethod
    def from_routing_kit_arc(route_arc: RouteArc):
        return OsmArc(
            osmWayId=route_arc.osmWayId,
            startOsmNodeId=route_arc.startOsmNodeId,
            endOsmNodeId=route_arc.endOsmNodeId,
            geometry=[point_lat_lon_to_geo_location(p) for p in route_arc.geometry],
            distance=route_arc.distance,
            duration=route_arc.duration,
        )


@public
class OsmRoutingKit(PathFinder[GeoCoords]):
    # FEATURE: support dist_cost, by setting low fixed speed limit (1mps), scaling not even necessary (1m = 1s);
    #  implement this in OSMDataProvider, where the time_cost parameter should be.
    def __init__(self, data: OsmChData, return_time_cost=True):
        """
        A PathFinder to find shortest paths using the RoutingKit ContractionHierarchy algorithm on the OSM intermediate
        data format.

        :param data: the graph and heuristic (not used) in the OSM intermediate format.
        :param return_time_cost: Whether to return the time cost (duration) or the distance cost. The shortest path is
        always calculated with respect to time cost.
        """
        # see https://lsogit.fzi.de/LSO/pyroutingkit/-/blob/main/src/cpp/lib/src/GraphPreparator.cpp?ref_type=heads#L30

        self.time_cost = return_time_cost

        self.graph_file = data.graph_file
        self.ch_file = data.ch_file

    def find_shortest_path(self, source: GeoCoords, destination: GeoCoords) -> Path[GeoCoords, OsmArc]:
        routing_service = RoutingService(self.graph_file, self.ch_file, MATCHING_RADIUS)
        route = routing_service.route(geo_location_to_point_lat_lon(source), geo_location_to_point_lat_lon(destination))
        return self._route_to_path(route)

    def _route_to_path(self, route: Route) -> Path[GeoCoords, OsmArc]:
        geometry_nodes = [p for arc in route.arcs for p in arc.geometry[:-1]] + route.arcs[-1].geometry[-1:]
        return Path(
            nodes=[point_lat_lon_to_geo_location(p) for p in geometry_nodes],
            edges=[OsmArc.from_routing_kit_arc(arc) for arc in route.arcs],
            cost=route.duration if self.time_cost else route.distance
        )
