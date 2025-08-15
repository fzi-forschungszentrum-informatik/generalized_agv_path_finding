from dataclasses import dataclass

from auto_all import public

from generalized_path_finding.nodes import VDA5050Position
from .action import Action
from .camelserial import CamelSerial


@public
@dataclass
class NodePosition(CamelSerial):
    """
    Geometric location of a node.
    """

    x: float
    """
    X position on the layout in reference to the global origin in meters.
    
    The global origin is the same for all layouts.   
    """

    y: float
    """
    Y position on the layout in reference to the global origin in meters.
    
    The global origin is the same for all layouts.
    """


@public
@dataclass
class VehicleTypeNodeProperties(CamelSerial):
    """
    Vehicle type specific properties for a node.
    """

    # The specification is missing the vehicle_type_id attribute, while its supposed description is in the description
    # of the VehicleTypeNodeProperties type. This is clearly a mistake as the property can also be found in the examples
    # listed in the second half of the specification.

    vehicle_type_id: str
    """
    Unique Id for type of vehicle to which these properties apply on this node. 
    Only one vehicleTypeNodeProperty can be declared per vehicle type per node.

    It is suggested that this be a combination of
    ``[factsheet.manufacturer].[factsheet.seriesName]``
    """

    theta: float | None = None
    """
    Absolute orientation of the vehicle on the node in reference to the global origin’s rotation.
    
    Range: [-Pi ... Pi]
    """

    actions: list[Action] | None = None
    """
    Holds actions that can be integrated into the order by the (third-party) master control system each time any 
    vehicle with the corresponding vehicle TypeId is sent an order/order update that contains this node. 
    The decision of which action is integrated into the order is the responsibility of the (third-party) master 
    control system. If no actions can be integrated, the attribute may be omitted. 
    """

    def __post_init__(self):
        if self.actions is None:
            self.actions = []


@public
@dataclass
class Node(CamelSerial):
    """
    Refers to VDA 5050 node definition. All properties that have the same name are meant to be semantically
    identical. However, the number of properties differs from VDA 5050 specification. Some properties are only
    meaningful as soon as an order is generated. Others only provide information for order generation (e.g.,
    routing) itself.
    """

    node_id: str
    """
    Unique identifier of the node across all layouts contained in this LIF file.

    Different LIF files, especially from different vehicle integrators, may contain duplicate nodeIds. In this case, 
    it is the responsibility of the (third-party) master control system to track whichever internal unique nodeId it 
    wishes to use, and to map this to a vehicle integrator‘s nodeId for its specific LIF.
    """

    node_position: NodePosition
    """
    Geometric location of the node.
    """

    vehicle_type_node_properties: list[VehicleTypeNodeProperties]
    """
    Vehicle type specific properties for this node.
    
    This attribute must not be empty. There must be an element for each vehicle type that may use this node. If no 
    element exists for a particular vehicle type, the (third-party) master control system must consider that node 
    invalid for use with that vehicle type.
    """

    node_name: str | None = None
    """
    Name of the node.
    
    This should only be for visualization purposes. 
    This attribute must not be used for any kind of identification or other logical purpose. 
    Therefore, this node name need not necessarily be unique.
    """

    node_description: str | None = None
    """
    Brief description of the node. 
    
    This should only ever be for visualization or diagnostic purposes.
    """

    map_id: str | None = None
    """
    Unique identification of the map in which the node oder node‘s position is referenced. 
    Each map has the same project specific global origin of coordinates.

    When a vehicle uses an elevator, e.g., leading from a departure floor to a target floor, it will disappear off 
    the map of the departure floor and spawn in the related lift node on the map of the target floor.
    """

    # integrity is checked in __post_init__ because this is run automatically, no matter whether the object is
    # created by reading from a camel dict or by constructing one manually.
    def __post_init__(self):
        if len(self.vehicle_type_node_properties) == 0:
            raise ValueError("Node.vehicle_type_node_properties must not be empty")

    def get_properties_for_vehicle_type(self, vehicle_type_id: str) -> VehicleTypeNodeProperties | None:
        """
        Get the properties for a specific vehicle type.

        :param vehicle_type_id: The vehicle type id.
        :return: The properties for the vehicle type, or None if not found.
        """
        for properties in self.vehicle_type_node_properties:
            if properties.vehicle_type_id == vehicle_type_id:
                return properties
        return None

    def get_vda5050(self) -> VDA5050Position:
        """
        Convert the node to a VDA5050 Position.
        """

        return VDA5050Position(self.node_position.x, self.node_position.y, self.map_id)
