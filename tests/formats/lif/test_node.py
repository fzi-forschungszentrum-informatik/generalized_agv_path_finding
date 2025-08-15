import pytest

from generalized_path_finding.formats.lif.node import Node, NodePosition, VehicleTypeNodeProperties
from generalized_path_finding.nodes import VDA5050Position


def test_post_init():
    # Test with valid vehicle_type_node_properties
    node_position = NodePosition(x=0.0, y=0.0)
    vehicle_properties = [VehicleTypeNodeProperties(vehicle_type_id="type1")]
    node = Node(
        node_id="node1",
        node_position=node_position,
        vehicle_type_node_properties=vehicle_properties,
    )
    assert node.vehicle_type_node_properties == vehicle_properties

    # Test with empty vehicle_type_node_properties
    with pytest.raises(ValueError, match="Node.vehicle_type_node_properties must not be empty"):
        Node(
            node_id="node2",
            node_position=node_position,
            vehicle_type_node_properties=[],
        )


def test_get_properties_for_vehicle_type():
    node_position = NodePosition(x=0.0, y=0.0)
    vehicle_properties = [
        VehicleTypeNodeProperties(vehicle_type_id="type1"),
        VehicleTypeNodeProperties(vehicle_type_id="type2"),
    ]
    node = Node(
        node_id="node1",
        node_position=node_position,
        vehicle_type_node_properties=vehicle_properties,
    )

    # Test finding an existing vehicle type
    properties = node.get_properties_for_vehicle_type("type1")
    assert properties is not None
    assert properties.vehicle_type_id == "type1"

    # Test finding a non-existing vehicle type
    properties = node.get_properties_for_vehicle_type("type3")
    assert properties is None


def test_get_vda5050():
    node_position = NodePosition(x=10.0, y=20.0)
    node = Node(
        node_id="node1",
        node_position=node_position,
        vehicle_type_node_properties=[VehicleTypeNodeProperties(vehicle_type_id="type1")],
        map_id="map123",
    )

    vda5050_position = node.get_vda5050()
    assert isinstance(vda5050_position, VDA5050Position)
    assert vda5050_position.x == 10.0
    assert vda5050_position.y == 20.0
    assert vda5050_position.map_id == "map123"
