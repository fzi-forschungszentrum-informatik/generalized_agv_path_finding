import pytest

from generalized_path_finding.formats.lif.station import Station, StationPosition


def test_post_init():
    # Test with valid interaction_node_ids
    station = Station(
        station_id="station1",
        interaction_node_ids=["node1", "node2"],
    )
    assert station.interaction_node_ids == ["node1", "node2"]

    # Test with empty interaction_node_ids
    with pytest.raises(ValueError, match="Station.interaction_node_ids must not be empty"):
        Station(
            station_id="station2",
            interaction_node_ids=[],
        )


def test_optional_attributes():
    # Test with all optional attributes defined
    position = StationPosition(x=1.0, y=2.0, theta=3.14)
    station = Station(
        station_id="station1",
        interaction_node_ids=["node1"],
        station_name="Test Station",
        station_description="A test station",
        station_height=5.0,
        station_position=position,
    )
    assert station.station_name == "Test Station"
    assert station.station_description == "A test station"
    assert station.station_height == 5.0
    assert station.station_position == position

    # Test with no optional attributes defined
    station = Station(
        station_id="station2",
        interaction_node_ids=["node1"],
    )
    assert station.station_name is None
    assert station.station_description is None
    assert station.station_height == 0
    assert station.station_position is None
