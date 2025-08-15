import math
import os
import pathlib

from generalized_path_finding.algorithms import OsmRoutingKit
from generalized_path_finding.formats.osm.osm_data_provider import OsmDataProvider, TransportMode
from generalized_path_finding.nodes import GeoCoords
from tests.constants import ORIGIN, DESTINATION, DISTANCE, DURATION, KPH_PER_MPS
from tests.util import remove_cache_file_if_coverage

current_path = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))


def local_path(relative_path):
    return str(current_path / relative_path)


def print_cost_ratio(path_dist, path_dur):
    print(
        f"dist/dur: {path_dist.cost} m / {path_dur.cost} s "
        f"= {path_dist.cost / path_dur.cost} m/s "
        f"= {path_dist.cost / path_dur.cost * 3.6} km/h"
    )


def test_output_format():
    data_provider = OsmDataProvider(local_path("../formats/osm/andorra-latest.osm.pbf"))
    osm_data = data_provider.get_osm_ch_data()

    path_finder = OsmRoutingKit(osm_data, return_time_cost=False)
    path = path_finder.find_shortest_path(ORIGIN, DESTINATION)

    assert isinstance(path.nodes[0], GeoCoords)


def test_distance_vs_duration():
    data_provider = OsmDataProvider(local_path("../formats/osm/andorra-latest.osm.pbf"))
    osm_data = data_provider.get_osm_ch_data()

    path_finder_dist = OsmRoutingKit(osm_data, return_time_cost=False)
    path_dist = path_finder_dist.find_shortest_path(ORIGIN, DESTINATION)

    path_finder_dur = OsmRoutingKit(osm_data, return_time_cost=True)
    path_dur = path_finder_dur.find_shortest_path(ORIGIN, DESTINATION)

    print_cost_ratio(path_dist, path_dur)

    assert path_dist.cost == DISTANCE
    assert math.isclose(path_dur.cost, DURATION, rel_tol=0.1)


def test_transport_mode():
    # this test sometimes fails on Windows when the whole suite is run, but never when it's run isolated

    dp_bike = OsmDataProvider(local_path("../formats/osm/andorra-latest.osm.pbf"),
                              transport_mode=TransportMode.BIKE)
    pf_bike_dist = OsmRoutingKit(dp_bike.get_osm_ch_data(), return_time_cost=False)
    path_dist = pf_bike_dist.find_shortest_path(ORIGIN, DESTINATION)

    pf_bike_dur = OsmRoutingKit(dp_bike.get_osm_ch_data(), return_time_cost=True)
    path_dur = pf_bike_dur.find_shortest_path(ORIGIN, DESTINATION)

    print_cost_ratio(path_dist, path_dur)

    # speed should be 15 kph (default in PyRoutingKit)
    speed_mps = 15 / KPH_PER_MPS
    assert math.isclose(path_dist.cost / path_dur.cost, speed_mps, rel_tol=0.01)

    dp_pedestrian = OsmDataProvider(local_path("../formats/osm/andorra-latest.osm.pbf"),
                                    transport_mode=TransportMode.PEDESTRIAN)
    pf_pedestrian_dist = OsmRoutingKit(dp_pedestrian.get_osm_ch_data(), return_time_cost=False)
    path_dist = pf_pedestrian_dist.find_shortest_path(ORIGIN, DESTINATION)

    pf_pedestrian_dur = OsmRoutingKit(dp_pedestrian.get_osm_ch_data(), return_time_cost=True)
    path_dur = pf_pedestrian_dur.find_shortest_path(ORIGIN, DESTINATION)

    print_cost_ratio(path_dist, path_dur)

    # speed should be 4 kph (default in PyRoutingKit)
    speed_mps = 4 / KPH_PER_MPS
    assert math.isclose(path_dist.cost / path_dur.cost, speed_mps, rel_tol=0.01)


def test_speed_override():
    speed_mps = 21 / KPH_PER_MPS
    dp_bike = OsmDataProvider(local_path("../formats/osm/andorra-latest.osm.pbf"),
                              transport_mode=TransportMode.BIKE, max_speed=speed_mps)
    pf_bike_dist = OsmRoutingKit(dp_bike.get_osm_ch_data(), return_time_cost=False)
    path_dist = pf_bike_dist.find_shortest_path(ORIGIN, DESTINATION)

    pf_bike_dur = OsmRoutingKit(dp_bike.get_osm_ch_data(), return_time_cost=True)
    path_dur = pf_bike_dur.find_shortest_path(ORIGIN, DESTINATION)

    print_cost_ratio(path_dist, path_dur)

    # speed should be same as override above
    assert math.isclose(path_dist.cost / path_dur.cost, speed_mps, rel_tol=0.01)

    speed_mps = 2 / KPH_PER_MPS
    dp_pedestrian = OsmDataProvider(local_path("../formats/osm/andorra-latest.osm.pbf"),
                                    transport_mode=TransportMode.PEDESTRIAN, max_speed=speed_mps)
    pf_ped_dist = OsmRoutingKit(dp_pedestrian.get_osm_ch_data(), return_time_cost=False)
    path_dist = pf_ped_dist.find_shortest_path(ORIGIN, DESTINATION)

    pf_ped_dur = OsmRoutingKit(dp_pedestrian.get_osm_ch_data(), return_time_cost=True)
    path_dur = pf_ped_dur.find_shortest_path(ORIGIN, DESTINATION)

    print_cost_ratio(path_dist, path_dur)

    # speed should be same as override above
    assert math.isclose(path_dist.cost / path_dur.cost, speed_mps, rel_tol=0.01)


def test_graph_conversion():
    # conversion takes 30 seconds -> don't do it every time tests are run but only if coverage is recorded
    remove_cache_file_if_coverage(local_path("../formats/osm/andorra-latest.osm.pbf_CAR.ch"))

    dp = OsmDataProvider(local_path("../formats/osm/andorra-latest.osm.pbf"))
    osm_data = dp.get_osm_ch_data()
    path_finder = OsmRoutingKit(osm_data)
    path = path_finder.find_shortest_path(ORIGIN, DESTINATION)
    assert path is not None
