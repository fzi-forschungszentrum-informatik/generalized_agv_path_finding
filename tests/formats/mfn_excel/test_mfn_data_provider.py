import math
import os
import pathlib

DIST_1_2 = math.hypot(1.5 - 2.3, 1.6 - 2.4)
DIST_2_3 = math.hypot(2.3 - 3, 2.4 - 2.4)

import pytest
from networkx.classes import MultiDiGraph

from generalized_path_finding.formats.mfn_excel import MfnDataProvider

current_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))


def test_graph_structure():
    dp = MfnDataProvider(current_path / "MFN_example.xlsx", fleet="Roboter")
    graph = dp.get_networkx_data().graph

    assert isinstance(graph, MultiDiGraph)
    assert set(graph.nodes) == {'1-E0', '2-E0', '3-E0', '1-E1'}
    assert set(graph.edges) == {
        ('1-E0', '2-E0', 'Path_1A'),
        ('2-E0', '1-E0', 'Path_1B'),
        ('2-E0', '3-E0', 'Path_2A'),
        ('3-E0', '2-E0', 'Path_2B'),
        ('1-E0', '1-E1', 'Connection1'),
        ('1-E1', '1-E0', 'Connection1')
    }


def test_edge_weights():
    dp = MfnDataProvider(current_path / "MFN_example.xlsx", fleet="Roboter")
    graph = dp.get_networkx_data().graph

    assert math.isclose(graph.edges['1-E0', '2-E0', 'Path_1A']['weight'], DIST_1_2, rel_tol=1e-6)
    assert math.isclose(graph.edges['2-E0', '1-E0', 'Path_1B']['weight'], DIST_1_2, rel_tol=1e-6)
    assert math.isclose(graph.edges['2-E0', '3-E0', 'Path_2A']['weight'], DIST_2_3, rel_tol=1e-6)
    assert math.isclose(graph.edges['3-E0', '2-E0', 'Path_2B']['weight'], DIST_2_3, rel_tol=1e-6)
    assert graph.edges['1-E0', '1-E1', 'Connection1']['weight'] == 0
    assert graph.edges['1-E1', '1-E0', 'Connection1']['weight'] == 0


def test_with_time_cost():
    speed = 2.0
    dp = MfnDataProvider(current_path / "MFN_example.xlsx", time_cost=True,
                         fleet_max_speed=speed, fleet="Roboter")
    graph = dp.get_networkx_data().graph

    assert isinstance(graph, MultiDiGraph)
    assert math.isclose(graph.edges['1-E0', '2-E0', 'Path_1A']['weight'], DIST_1_2 / speed, rel_tol=1e-6)
    assert math.isclose(graph.edges['2-E0', '1-E0', 'Path_1B']['weight'], DIST_1_2 / speed, rel_tol=1e-6)
    assert math.isclose(graph.edges['2-E0', '3-E0', 'Path_2A']['weight'], DIST_2_3 / speed, rel_tol=1e-6)
    assert math.isclose(graph.edges['3-E0', '2-E0', 'Path_2B']['weight'], DIST_2_3 / 0.5, rel_tol=1e-6)  # local limit
    assert graph.edges['1-E0', '1-E1', 'Connection1']['weight'] == 90
    assert graph.edges['1-E1', '1-E0', 'Connection1']['weight'] == 90


def test_impute_fleet():
    dp = MfnDataProvider(current_path / "MFN_Roboter_only.xlsx")
    dp.get_networkx_data()  # make it actually convert the graph and select the fleet

    assert dp.fleet == "roboter"


def test_multiple_vehicles():
    dp_robot = MfnDataProvider(current_path / "MFN_example.xlsx", fleet="Roboter")
    graph_robot = dp_robot.get_networkx_data().graph

    assert isinstance(graph_robot, MultiDiGraph)
    assert set(graph_robot.nodes) == {'1-E0', '2-E0', '3-E0', '1-E1'}
    assert set(graph_robot.edges) == {
        ('1-E0', '2-E0', 'Path_1A'),
        ('2-E0', '1-E0', 'Path_1B'),
        ('2-E0', '3-E0', 'Path_2A'),
        ('3-E0', '2-E0', 'Path_2B'),
        ('1-E0', '1-E1', 'Connection1'),
        ('1-E1', '1-E0', 'Connection1')
    }

    dp_pedestrian = MfnDataProvider(current_path / "MFN_example.xlsx", fleet="Besucher")
    graph_pedestrian = dp_pedestrian.get_networkx_data().graph

    assert isinstance(graph_pedestrian, MultiDiGraph)
    assert set(graph_pedestrian.nodes) == {'1-E0', '2-E0', '3-E0', '1-E1'}
    assert set(graph_pedestrian.edges) == {
        ('1-E0', '1-E1', 'Connection1'),
        ('1-E1', '1-E0', 'Connection1')
    }

    # no fleet given while there are multiple fleets in the file
    with pytest.raises(RuntimeError) as e:
        data_provider = MfnDataProvider(current_path / "MFN_example.xlsx")
        data_provider.get_networkx_data()  # make it actually convert the graph

    assert "fleet" in str(e)

    # non-occurring fleet given
    with pytest.warns(UserWarning) as record:
        data_provider = MfnDataProvider(current_path / "MFN_example.xlsx", fleet="Aliens")
        data_provider.get_networkx_data()  # make it actually convert the graph

    assert len(record) == 1
    assert "fleet" in str(record[0].message)


def test_heuristic():
    dp = MfnDataProvider(current_path / "MFN_example.xlsx", fleet="Roboter")

    heuristic = dp.get_networkx_data().heuristic

    assert callable(heuristic)
    # Test heuristic between nodes 1-E0 and 2-E0
    assert math.isclose(heuristic("1-E0", "2-E0"), DIST_1_2, rel_tol=1e-6)


def test_heuristic_with_time_cost():
    speed = 0.5
    dp = MfnDataProvider(current_path / "MFN_example.xlsx",
                         time_cost=True,
                         fleet_max_speed=speed,
                         fleet="Roboter")

    heuristic = dp.get_networkx_data().heuristic

    assert callable(heuristic)
    # Test heuristic between nodes 1-E0 and 2-E0 with time cost
    assert math.isclose(heuristic("1-E0", "2-E0"), math.hypot(1.5 - 2.3, 1.6 - 2.4) / speed, rel_tol=1e-6)


def test_priority_factor():
    dp = MfnDataProvider(current_path / "MFN_example.xlsx", fleet="Roboter",
                         priority_factor=lambda x: x * x if x is not None else 0.5)
    graph = dp.get_networkx_data().graph

    assert math.isclose(graph.edges['1-E0', '2-E0', 'Path_1A']['weight'], DIST_1_2, rel_tol=1e-6)
    assert math.isclose(graph.edges['2-E0', '1-E0', 'Path_1B']['weight'], DIST_1_2, rel_tol=1e-6)
    assert math.isclose(graph.edges['2-E0', '3-E0', 'Path_2A']['weight'], DIST_2_3 * 4, rel_tol=1e-6)
    assert math.isclose(graph.edges['3-E0', '2-E0', 'Path_2B']['weight'], DIST_2_3 * 0.5,
                        rel_tol=1e-6)  # no priority given

    # no priority factor mapping given, ignore priority
    dp = MfnDataProvider(current_path / "MFN_example.xlsx", fleet="Roboter")
    graph = dp.get_networkx_data().graph

    assert math.isclose(graph.edges['1-E0', '2-E0', 'Path_1A']['weight'], DIST_1_2, rel_tol=1e-6)
    assert math.isclose(graph.edges['2-E0', '1-E0', 'Path_1B']['weight'], DIST_1_2, rel_tol=1e-6)
    assert math.isclose(graph.edges['2-E0', '3-E0', 'Path_2A']['weight'], DIST_2_3, rel_tol=1e-6)
    assert math.isclose(graph.edges['3-E0', '2-E0', 'Path_2B']['weight'], DIST_2_3, rel_tol=1e-6)  # no priority given


def test_heuristic_with_priority():
    dp = MfnDataProvider(current_path / "MFN_example.xlsx", fleet="Roboter",
                         priority_factor=lambda x: 2)

    heuristic = dp.get_networkx_data().heuristic

    assert callable(heuristic)
    assert math.isclose(heuristic("1-E0", "2-E0"), DIST_1_2 * 2, rel_tol=1e-6)


def test_infinite_speed():
    dp = MfnDataProvider(current_path / "MFN_example.xlsx",
                         time_cost=True,
                         fleet_max_speed=float("infinity"),
                         fleet="Roboter")

    with pytest.raises(ValueError) as e:
        dp.get_networkx_data()
    assert "speed" in str(e)
