import json
import math
import os
from pathlib import Path

from generalized_path_finding.formats.lif import LIF

current_path = Path(os.path.dirname(os.path.realpath(__file__)))


def test_approximate_length():
    """
    Test that the approximate length of the trajectory can be calculated with sufficient accuracy
    """

    with open(current_path / 'LIF_trajectory.json', 'r') as f:
        data = json.load(f)
    lif = LIF.from_camel_dict(data)

    lengths = [lif.layouts[0].edges[i].vehicle_type_edge_properties[0].trajectory.approximate_length() for i in
          range(2)]

    correct_length = 5.84
    eps = 0.01  # require approximation with at most 1 % relative error

    assert math.isclose(lengths[0], correct_length, rel_tol=eps)
    assert math.isclose(lengths[1], correct_length, rel_tol=eps)


def test_degree_1_trajectory_length():
    """
    Test that the length of a degree 1 trajectory is calculated exactly.
    """
    from generalized_path_finding.formats.lif.trajectory import Trajectory, ControlPoint

    control_points = [
        ControlPoint(x=0.0, y=0.0),
        ControlPoint(x=3.0, y=4.0),  # Distance = 5.0
        ControlPoint(x=0.0, y=8.0)  # Distance = 5.0
    ]
    trajectory = Trajectory(
        knot_vector=[0.0, 0.0, 1.0, 1.0],
        control_points=control_points,
        degree=1
    )

    expected_length = 10.0  # Exact length
    calculated_length = trajectory.approximate_length()

    assert math.isclose(calculated_length, expected_length, rel_tol=1e-9), \
        f"Expected {expected_length}, but got {calculated_length}"
