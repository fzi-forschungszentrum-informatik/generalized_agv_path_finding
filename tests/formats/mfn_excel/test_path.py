import pytest
from beartype.roar import BeartypeCallHintParamViolation

from generalized_path_finding.formats.mfn_excel.path import Path


def test_post_init():
    # Test valid fleet list parsing
    path = Path(
        name="path1",
        origin_node_name="node1",
        destination_node_name="node2",
        network="network1",
        origin_id=1,
        dest_id=2,
        prio=1,
        speed_limit_mps=5.0,
        description="description",
        color="blue",
        controls=None,
        pedestrians="pedestrians1",
        fleets="fleet1 | fleet2",
    )
    assert path.fleet_list == ["fleet1", "fleet2"]

    # Test empty fleet list
    path = Path(
        name="path2",
        origin_node_name="node1",
        destination_node_name="node2",
        network="network1",
        origin_id=1,
        dest_id=2,
        prio=1,
        speed_limit_mps=5.0,
        description="description",
        color="blue",
        controls=None,
        pedestrians="pedestrians1",
        fleets="",
    )
    assert path.fleet_list == []


def test_supports_fleet():
    path = Path(
        name="path1",
        origin_node_name="node1",
        destination_node_name="node2",
        network="network1",
        origin_id=1,
        dest_id=2,
        prio=1,
        speed_limit_mps=5.0,
        description="description",
        color="blue",
        controls=None,
        pedestrians="pedestrians1",
        fleets="fleet1 | fleet2",
    )

    # Test fleet supported
    assert path.supports_fleet("fleet1") is True
    assert path.supports_fleet("fleet2") is True

    # Test fleet not supported
    assert path.supports_fleet("fleet3") is False

    # Test fleet with extra whitespace
    assert path.supports_fleet(" fleet1 ") is True
    assert path.supports_fleet("fleet2 ") is True

    # Test case-insensitivity
    assert path.supports_fleet("FLEET1") is True
    assert path.supports_fleet("Fleet2") is True


def test_missing_inputs():
    with pytest.raises(BeartypeCallHintParamViolation):
        # noinspection PyTypeChecker
        Path(
            name="path2",
            origin_node_name="node1",
            destination_node_name="node2",
            network="network1",
            origin_id=1,
            dest_id=2,
            prio=1,
            speed_limit_mps=5.0,
            description="description",
            color="blue",
            controls=None,
            pedestrians="pedestrians1",
            fleets=None,  # Should be a string
        )
