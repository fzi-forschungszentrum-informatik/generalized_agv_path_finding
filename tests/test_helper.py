import math
import os
from pathlib import Path

from generalized_path_finding.algorithms import AStar, NxRoutingKit, OsmRoutingKit
from generalized_path_finding.formats.lif import LifDataProvider
from generalized_path_finding.formats.mfn_excel import MfnDataProvider
from generalized_path_finding.formats.osm.osm_data_provider import OsmDataProvider
from generalized_path_finding.helper import create_path_finder, Algorithm
from generalized_path_finding.model import PathFinder
from tests.constants import EXACT_ORIGIN, EXACT_DESTINATION, ORIGIN, DESTINATION, DURATION
from tests.formats.mfn_excel.test_mfn_data_provider import DIST_1_2, DIST_2_3

current_path = Path(os.path.dirname(os.path.abspath(__file__)))


def test_create_path_finder_for_lif_and_astar():
    data_provider = LifDataProvider(current_path / "formats/lif/LIF_4_4_MAPF.json")
    algo = create_path_finder(data_provider, Algorithm.A_STAR)
    assert isinstance(algo, AStar)

    p = algo.find_shortest_path("N_0_2", "N_3_3")
    assert p is not None
    assert p.cost == 4
    assert p.nodes == ['N_0_2', 'N_1_2', 'N_2_2', 'N_3_2', 'N_3_3']
    assert p.edges == ['E-0_2-1_2', 'E-1_2-2_2', 'E-2_2-3_2', 'E-3_2-3_3']


def test_create_path_finder_for_lif_and_routing_kit():
    data_provider = LifDataProvider(current_path / "formats/lif/LIF_4_4_MAPF.json")
    algo = create_path_finder(data_provider, Algorithm.ROUTING_KIT)

    assert isinstance(algo, PathFinder)
    assert isinstance(algo, NxRoutingKit)  # maybe too specific

    p = algo.find_shortest_path("N_0_2", "N_3_3")
    assert p is not None
    assert p.cost == 4
    assert p.nodes == ['N_0_2', 'N_1_2', 'N_2_2', 'N_3_2', 'N_3_3']
    assert p.edges == ['E-0_2-1_2', 'E-1_2-2_2', 'E-2_2-3_2', 'E-3_2-3_3']


def test_create_path_finder_for_mfn_and_astar():
    data_provider = MfnDataProvider(current_path / "formats/mfn_excel/2025-04-04_Template_Routing_Input_UKF.xlsx",
                                    fleet="Roboter")
    algo = create_path_finder(data_provider, Algorithm.A_STAR)
    assert isinstance(algo, AStar)

    p = algo.find_shortest_path("3-E0", "1-E1")

    assert p is not None
    assert math.isclose(p.cost, DIST_1_2 + DIST_2_3, rel_tol=1e-6)
    assert p.nodes == ['3-E0', '2-E0', '1-E0', '1-E1']
    assert p.edges == ['Path_2B', 'Path_1B', 'Connection1']


def test_create_path_finder_for_mfn_and_routing_kit():
    data_provider = MfnDataProvider(current_path / "formats/mfn_excel/2025-04-04_Template_Routing_Input_UKF.xlsx",
                                    fleet="Roboter")
    algo = create_path_finder(data_provider, Algorithm.ROUTING_KIT)
    assert isinstance(algo, PathFinder)
    assert isinstance(algo, NxRoutingKit)  # maybe too specific

    p = algo.find_shortest_path("3-E0", "1-E1")
    assert p is not None
    assert math.isclose(p.cost, DIST_1_2 + DIST_2_3, rel_tol=1e-6)
    assert p.nodes == ['3-E0', '2-E0', '1-E0', '1-E1']
    assert p.edges == ['Path_2B', 'Path_1B', 'Connection1']


def test_create_path_finder_for_osm_and_routing_kit():
    data_provider = OsmDataProvider(current_path / "formats/osm/andorra-latest.osm.pbf")
    algo = create_path_finder(data_provider, Algorithm.ROUTING_KIT)
    assert isinstance(algo, PathFinder)
    assert isinstance(algo, OsmRoutingKit)  # maybe too specific

    p = algo.find_shortest_path(ORIGIN, DESTINATION)
    assert p is not None
    assert math.isclose(p.cost, DURATION, rel_tol=1e-6)


def test_create_path_finder_for_osm_and_astar():
    data_provider = OsmDataProvider(current_path / "formats/osm/andorra-latest.osm.pbf")
    algo = create_path_finder(data_provider, Algorithm.A_STAR)
    assert isinstance(algo, AStar)

    p = algo.find_shortest_path(EXACT_ORIGIN, EXACT_DESTINATION)
    assert p is not None
    # assert math.isclose(p.cost, DURATION, rel_tol=1e-6)

    # Frankly, when converting from OSM to NetworkX the edge selection and speed limits do not match those in
    # RoutingKit exactly, although the graph conversion is mimicking the implementation in RoutingKit.
    # This is why DISTANCE is slightly longer and DURATION is slightly shorter with AStar than with RoutingKit.


def test_create_path_finder_with_auto():
    data_provider = OsmDataProvider(current_path / "formats/osm/andorra-latest.osm.pbf")
    algo = create_path_finder(data_provider)
    assert isinstance(algo, OsmRoutingKit)

    data_provider = LifDataProvider(current_path / "formats/lif/LIF_4_4_MAPF.json")
    algo = create_path_finder(data_provider)
    assert isinstance(algo, AStar)

    # few nodes
    data_provider = MfnDataProvider(current_path / "formats/mfn_excel/2025-04-04_Template_Routing_Input_UKF.xlsx",
                                    fleet="Roboter")
    algo = create_path_finder(data_provider)
    assert isinstance(algo, AStar)

    # many nodes
    data_provider = MfnDataProvider(current_path / "formats/mfn_excel/MFN_11000_nodes.xlsx",
                                    fleet="Roboter")
    algo = create_path_finder(data_provider)
    assert isinstance(algo, NxRoutingKit)
