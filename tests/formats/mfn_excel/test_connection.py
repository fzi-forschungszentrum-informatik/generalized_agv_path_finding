import pytest
from beartype.roar import BeartypeCallHintParamViolation

from generalized_path_finding.formats.mfn_excel.connection import Connection


def test_post_init():
    # Test valid fleet list parsing
    connection = Connection(
        name="conn1",
        origin_node_name="node1",
        destination_node_name="node2",
        cal_trans_duration_seconds=30,
        origin_controls="controls1",
        origin_network="network1",
        destination_network="network2",
        description="description",
        pedestrians="pedestrians1",
        fleets="fleet1 | fleet2",
        orientation="orientation1",
        comment="comment1",
    )
    assert connection.fleet_list == ["fleet1", "fleet2"]

    # Test empty fleet list
    connection = Connection(
        name="conn2",
        origin_node_name="node1",
        destination_node_name="node2",
        cal_trans_duration_seconds=30,
        origin_controls="controls1",
        origin_network="network1",
        destination_network="network2",
        description="description",
        pedestrians="pedestrians1",
        fleets="",
        orientation="orientation1",
        comment="comment1",
    )
    assert connection.fleet_list == []


def test_supports_fleet():
    connection = Connection(
        name="conn1",
        origin_node_name="node1",
        destination_node_name="node2",
        cal_trans_duration_seconds=30,
        origin_controls="controls1",
        origin_network="network1",
        destination_network="network2",
        description="description",
        pedestrians="pedestrians1",
        fleets="fleet1 | fleet2",
        orientation="orientation1",
        comment="comment1",
    )

    # Test fleet supported
    assert connection.supports_fleet("fleet1") is True
    assert connection.supports_fleet("fleet2") is True

    # Test fleet not supported
    assert connection.supports_fleet("fleet3") is False

    # Test fleet with extra whitespace
    assert connection.supports_fleet(" fleet1 ") is True
    assert connection.supports_fleet("fleet2 ") is True

    # Test case-insensitivity
    assert connection.supports_fleet("FLEET1") is True
    assert connection.supports_fleet("Fleet2") is True


def test_missing_inputs():
    with pytest.raises(BeartypeCallHintParamViolation):
        # noinspection PyTypeChecker
        Connection(
            name="conn2",
            origin_node_name="node1",
            destination_node_name="node2",
            cal_trans_duration_seconds=30,
            origin_controls="controls1",
            origin_network="network1",
            destination_network="network2",
            description="description",
            pedestrians="pedestrians1",
            fleets=None,  # Should be a string
            orientation="orientation1",
            comment="comment1",
        )
