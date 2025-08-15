import pytest

from generalized_path_finding.nodes.vda5050_position import VDA5050Position


def test_compute_euclidean_distance_vda5050():
    pos_a = VDA5050Position(0.0, 0.0, "map")
    pos_b = VDA5050Position(1.0, 2.0, "map")
    assert VDA5050Position.euclidean_distance(pos_a, pos_b) == pytest.approx(2.236, abs=0.001)


def test_compute_euclidean_distance_vda5050_same_position():
    pos_a = VDA5050Position(0.0, 0.0, "map")
    assert VDA5050Position.euclidean_distance(pos_a, pos_a) == 0.0
