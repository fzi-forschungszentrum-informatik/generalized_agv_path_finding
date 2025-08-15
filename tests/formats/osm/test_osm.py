import os
from pathlib import Path

from pyroutingkit import RoutingService, Route, PointLatLon

from generalized_path_finding.formats.osm.osm_data_provider import OsmDataProvider

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
def local_path(relative_path):
    return str(current_path / relative_path)


def test_preparator():
    dp = OsmDataProvider(local_path("andorra-latest.osm.pbf"))
    ch_data = dp.get_osm_ch_data()

    router = RoutingService(local_path(ch_data.graph_file),
                            local_path(ch_data.ch_file),
                            1000)
    origin = PointLatLon(42.46333811337092, 1.489878394942694)
    destination = PointLatLon(42.50946473317848, 1.5397046939511791)

    route: Route = router.route(origin, destination)

    print(route.duration, route.distance)
    for arc in route.arcs:
        print(arc.duration, arc.distance, arc.osmWayId, arc.startOsmNodeId, arc.endOsmNodeId)


if __name__ == "__main__":
    test_preparator()