import pytest

from generalized_path_finding.formats.lif.edge import Edge, VehicleTypeEdgeProperties


def test_post_init():
    # Test with valid vehicle_type_edge_properties
    vehicle_properties = [VehicleTypeEdgeProperties(vehicle_type_id="type1", rotation_allowed=True)]
    edge = Edge(
        edge_id="edge1",
        start_node_id="node1",
        end_node_id="node2",
        vehicle_type_edge_properties=vehicle_properties,
    )
    assert edge.vehicle_type_edge_properties == vehicle_properties

    # Test with empty vehicle_type_edge_properties
    with pytest.raises(ValueError, match="Edge.vehicle_type_edge_properties must not be empty"):
        Edge(
            edge_id="edge2",
            start_node_id="node1",
            end_node_id="node2",
            vehicle_type_edge_properties=[],
        )


def test_get_properties_for_vehicle_type():
    vehicle_properties = [
        VehicleTypeEdgeProperties(vehicle_type_id="type1", rotation_allowed=True),
        VehicleTypeEdgeProperties(vehicle_type_id="type2", rotation_allowed=False),
    ]
    edge = Edge(
        edge_id="edge1",
        start_node_id="node1",
        end_node_id="node2",
        vehicle_type_edge_properties=vehicle_properties,
    )

    # Test finding an existing vehicle type
    properties = edge.get_properties_for_vehicle_type("type1")
    assert properties is not None
    assert properties.vehicle_type_id == "type1"
    assert properties.rotation_allowed is True

    # Test finding a non-existing vehicle type
    properties = edge.get_properties_for_vehicle_type("type3")
    assert properties is None
