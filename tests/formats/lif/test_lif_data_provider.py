import math
import os
from math import sqrt
from pathlib import Path

import pytest
from beartype.roar import BeartypeCallHintParamViolation
from networkx.classes import MultiDiGraph

from generalized_path_finding.formats.lif.lif_data_provider import DistanceType
from generalized_path_finding.formats.lif.lif_data_provider import LifDataProvider

current_path = Path(os.path.dirname(os.path.realpath(__file__)))


def test_graph_structure():
    data_provider = LifDataProvider(current_path / "LIF_single_edge.json")
    graph = data_provider._get_graph()

    assert isinstance(graph, MultiDiGraph)
    assert list(graph.nodes) == ['N1', 'N2']
    assert list(graph.edges) == [('N1', 'N2', 'E-1-2')]
    assert graph.edges['N1', 'N2', 'E-1-2']['weight'] == sqrt(2)


def test_impute_vehicle_type():
    data_provider = LifDataProvider(current_path / "LIF_single_edge.json")
    _graph = data_provider._get_graph()  # make it actually convert the graph and select the vehicle type

    assert data_provider.vehicle_type_id == "robot"


def test_multiple_vehicle_types():
    dp_robot = LifDataProvider(current_path / "LIF_multiple_vehicle_types.json", vehicle_type_id="robot")
    graph_robot = dp_robot._get_graph()
    assert isinstance(graph_robot, MultiDiGraph)
    assert set(graph_robot.nodes) == {'N1', 'N2', 'N3'}
    assert set(graph_robot.edges) == {('N1', 'N2', 'E-1-2')}

    dp_human = LifDataProvider(current_path / "LIF_multiple_vehicle_types.json", vehicle_type_id="human")
    graph_human = dp_human._get_graph()
    assert isinstance(graph_human, MultiDiGraph)
    assert set(graph_human.nodes) == {'N1', 'N2', 'N3'}  # all nodes are always created
    assert set(graph_human.edges) == {('N1', 'N3', 'E-1-3')}  # E-1-2 is filtered out because human cannot use N2

    # no vehicle type id given while there are multiple vehicle types in the file
    with pytest.raises(RuntimeError) as e:
        data_provider = LifDataProvider(current_path / "LIF_multiple_vehicle_types.json")
        _graph = data_provider._get_graph()  # make it actually convert the graph

    assert "more than one vehicle type" in str(e)

    # non-occurring vehicle type id given
    with pytest.warns(UserWarning) as record:
        data_provider = LifDataProvider(current_path / "LIF_multiple_vehicle_types.json", vehicle_type_id="aliens")
        _graph = data_provider._get_graph()  # make it actually convert the graph

    assert len(record) == 1
    assert "vehicle type" in str(record[0].message)


def test_manhattan_distance():
    data_provider = LifDataProvider(current_path / "LIF_single_edge.json", distance_type=DistanceType.Manhattan)
    graph = data_provider._get_graph()

    assert isinstance(graph, MultiDiGraph)
    assert graph.edges['N1', 'N2', 'E-1-2']['weight'] == 2  # Manhattan distance between (0, 0) and (1, 1)


def test_time_cost_with_global_limit():
    speed = 0.5
    data_provider = LifDataProvider(
        current_path / "LIF_single_edge.json",
        time_cost=True,
        vehicle_max_speed=speed
    )
    graph = data_provider._get_graph()

    assert isinstance(graph, MultiDiGraph)
    assert math.isclose(graph.edges['N1', 'N2', 'E-1-2']['weight'], sqrt(2) / speed,
                        rel_tol=1e-6)  # Euclidean distance divided by speed


def test_time_cost_with_individual_limit():
    data_provider = LifDataProvider(
        current_path / "LIF_single_edge.json",
        time_cost=True
    )
    graph = data_provider._get_graph()

    assert isinstance(graph, MultiDiGraph)
    # speed on this single edge is 1.0 in LIF file
    assert graph.edges['N1', 'N2', 'E-1-2']['weight'] == sqrt(2)  # Euclidean distance divided by speed


def test_trajectory_or_euclidean():
    data_provider = LifDataProvider(
        current_path / "LIF_trajectory.json",
        distance_type=DistanceType.TrajectoryOrEuclidean
    )
    graph = data_provider._get_graph()

    assert isinstance(graph, MultiDiGraph)
    # trajectory
    assert math.isclose(graph.edges['N1', 'N2', 'E-1-2']['weight'], 5.84, rel_tol=0.01)
    # euclidean
    assert math.isclose(graph.edges['N1', 'N3', 'E-1-3']['weight'], math.hypot(5, 5), rel_tol=1e-6)


def test_heuristic():
    data_provider = LifDataProvider(current_path / "LIF_single_edge.json", distance_type=DistanceType.Euclidean)

    heuristic = data_provider._get_heuristic()

    assert callable(heuristic)
    assert math.isclose(heuristic("N1", "N2"), sqrt(2), rel_tol=1e-6)

    data_provider = LifDataProvider(current_path / "LIF_single_edge.json", distance_type=DistanceType.Manhattan)

    heuristic = data_provider._get_heuristic()

    assert callable(heuristic)
    assert math.isclose(heuristic("N1", "N2"), 2, rel_tol=1e-6)

    data_provider = LifDataProvider(current_path / "LIF_single_edge.json",
                                    distance_type=DistanceType.TrajectoryOrEuclidean)

    heuristic = data_provider._get_heuristic()

    assert callable(heuristic)
    assert math.isclose(heuristic("N1", "N2"), sqrt(2), rel_tol=1e-6)


def test_heuristic_with_time_cost():
    speed = 0.5
    data_provider = LifDataProvider(current_path / "LIF_single_edge.json", time_cost=True, vehicle_max_speed=speed,
                                    distance_type=DistanceType.Euclidean)

    heuristic = data_provider._get_heuristic()

    assert callable(heuristic)
    assert math.isclose(heuristic("N1", "N2"), sqrt(2) / speed, rel_tol=1e-6)

    data_provider = LifDataProvider(current_path / "LIF_single_edge.json", time_cost=True, vehicle_max_speed=speed,
                                    distance_type=DistanceType.Manhattan)

    heuristic = data_provider._get_heuristic()

    assert callable(heuristic)
    assert math.isclose(heuristic("N1", "N2"), 2 / speed, rel_tol=1e-6)

    data_provider = LifDataProvider(current_path / "LIF_single_edge.json", time_cost=True, vehicle_max_speed=speed,
                                    distance_type=DistanceType.TrajectoryOrEuclidean)

    heuristic = data_provider._get_heuristic()

    assert callable(heuristic)
    assert math.isclose(heuristic("N1", "N2"), sqrt(2) / speed, rel_tol=1e-6)


def test_infinite_speed():
    data_provider = LifDataProvider(current_path / "LIF_single_edge.json", time_cost=True,
                                    vehicle_max_speed=float("infinity"))
    # there can be a usable heuristic here
    assert data_provider.get_networkx_data() is not None



def test_invalid_distance_type():
    with pytest.raises(BeartypeCallHintParamViolation) as e:
        # noinspection PyTypeChecker
        _data_provider = LifDataProvider(current_path / "LIF_single_edge.json", distance_type=5)

    assert "DistanceType" in str(e)
