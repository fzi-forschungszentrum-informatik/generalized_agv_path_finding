from dataclasses import dataclass
from enum import Enum

from auto_all import public

from .action import Action
from .camelserial import CamelSerial
from .trajectory import Trajectory


@public
class OrientationType(str, Enum):
    """
    Frame of reference of an orientation.

    If not defined, the default value is `TANGENTIAL`.
    """

    GLOBAL = "GLOBAL"
    """
    Relative to the global project specific map coordinate system.
    """

    TANGENTIAL = "TANGENTIAL"
    """
    Tangential to the edge.
    """

@public
class RotationAllowed(str, Enum):
    """
    Allowed directions of rotation for a vehicle.
    """

    NONE = 'NONE'
    """
    Rotation not allowed.
    """

    CCW = 'CCW'
    """
    Counter-clockwise rotation allowed (positive).
    """

    CW = 'CW'
    """
    Clockwise rotation allowed (negative).
    """

    BOTH = 'BOTH'
    """
    Both clockwise and counter-clockwise rotation allowed.
    """


@public
@dataclass
class LoadRestriction(CamelSerial):
    """
    Describes the load restriction on an edge for a vehicle of a specific `vehicle_type_id`.
    """

    unloaded: bool
    """
    `True`: This edge may be used by an unloaded vehicle with the corresponding vehicleTypeId.
    
    `False`: This edge must not be used by an unloaded vehicle with the corresponding vehicleTypeId.
    """

    loaded: bool
    """
    `True`: This edge may be used by a loaded vehicle
    with the corresponding vehicleTypeId.
    
    `False`: This edge must not be used by a loaded
    vehicle with the corresponding vehicleTypeId.
    """

    load_set_names: list[str] | None = None
    """
    List of load sets that may be transported by the vehicle on this edge. 
    
    The (third-party) master control system must evaluate this attribute only if the attribute loaded is set to true.
    
    If not defined or the attribute is empty, it means that all load sets supported by the vehicle loadSets are 
    allowed. The same names for the load sets must be used here as are given in the factsheet of the respective 
    vehicle (Factsheet attribute: ``[loadSets.setName]``).
    """


@public
@dataclass
class VehicleTypeEdgeProperties(CamelSerial):
    """
    Vehicle type specific properties for an edge.
    """

    vehicle_type_id: str
    """
    Unique Id for the type of vehicle to which these properties apply on this edge. 
    
    Only one vehicleTypeEdge Property can be declared per vehicle type per edge.
    
    It is suggested that this be a combination of 
    ``[factsheet.manufacturer].[factsheet.seriesName]``
    """

    rotation_allowed: bool
    """
    `True`: rotation is allowed on the edge. 
    The (third-party) master control system must assume that the vehicle will rotate in any direction along the edge at 
    any point. The (third-party) master control system is responsible for avoiding issuing commands which will result 
    in invalid or conflicting commands to other vehicles also under its control (e.g. deadlocks, potential collision).

    `False`: rotation is not allowed on the edge.
    """

    vehicle_orientation: float | None = None
    """
    Orientation of the vehicle on the edge in radians. 
    
    The value orientationType defines if it has to be interpreted relative to the global project specific map 
    coordinate system or tangential to the edge. 
    In case of interpreted tangential to the edge 0.0 = forwards and Pi = backwards. 
    Example: orientation Pi/2 rad will lead to a rotation of 90 degrees. 
    
    If the vehicle starts in a different orientation, rotate the vehicle on the edge to the desired orientation if 
    `rotation_allowed` is set to `True`.

    If `rotation_allowed` is `False`, rotate before entering the edge (assuming the start node allows rotation).
    If no trajectory is defined, apply the orientation to the direct path between the two connecting nodes of the edge. 
    If a trajectory is defined for the edge, apply the orientation to the trajectory
    """

    orientation_type: OrientationType | None = OrientationType.TANGENTIAL
    """
    Frame of reference for the `vehicle_orientation`.
    
    If not defined, the default value is `OrientationType.TANGENTIAL`.
    """

    rotation_at_start_node_allowed: RotationAllowed | None = RotationAllowed.BOTH
    """
    Allowed directions of rotation for the vehicle at the start node.
    
    If not defined, the default value is `RotationAllowed.BOTH`.
    """

    rotation_at_end_node_allowed: RotationAllowed | None = RotationAllowed.BOTH
    """
    Allowed directions of rotation for the vehicle at the end node.
    
    If not defined, the default value is `RotationAllowed.BOTH`.
    """

    max_speed: float | None = None
    """
    Permitted maximum speed on the edge in meters per second. 
    
    Speed is defined by the fastest measurement of the vehicle.
    
    If not defined, no limitation.
    """

    max_rotation_speed: float | None = None
    """
    Maximum rotation speed in radians per second.
    
    If not defined, no limitation.
    """

    min_height: float | None = None
    """
    Permitted minimal height of the load handling device on the edge in meters.
    
    If not defined, no limitation.
    """

    max_height: float | None = None
    """
    Permitted maximum height of the vehicle, including the load, on the edge in meters.
    
    If not defined, no limitation.
    """

    load_restriction: LoadRestriction | None = None
    """
    Describes the load restriction on this edge for a vehicle of the corresponding `vehicle_type_id`.

    If not defined, the edge can be used by both an unloaded and loaded vehicle with the corresponding 
    `vehicle_type_id`.
    """

    actions: list[Action] | None = None
    """
    Holds actions that can be integrated into the order by the (third-party) master control system each time any 
    vehicle with the corresponding vehicleTypeId is sent an order/order update that contains this edge.

    If no actions must be integrated, the attribute can be omitted.
    """

    trajectory: Trajectory | None = None
    """
    Trajectory for this edge as a NURBS. 
    
    Defines the curve on which the vehicle should move between the start node node and the end node. 
    Can be omitted if the vehicle cannot process trajectories or if the vehicle plans its own trajectory. 

    The trajectory is not required, but if it is not provided, the (third-party) master control system may
    not be able to determine whether different vehicles from the same or a different manufacturer are
    colliding.
    """

    reentry_allowed: bool | None = True
    """
    `True`: Vehicles of the corresponding vehicleTypeId are allowed to enter into automatic management by the 
    ( third-party) master control system while on this edge.
    
    `False`: Vehicles of the corresponding vehicleTypeId are not allowed to enter into automatic management by the 
    (third-party) master control system while on this edge. 
    
    If not defined, the default is `True`.
    """


@public
@dataclass
class Edge(CamelSerial):
    """
    Refers to VDA 5050 edge definition.
    All properties that have the same name are meant to be semantically identical.

    Edges are directional, i.e. it does not allow travel from end to start.

    The LIF only contains edges that can be used by at least one vehicle type.
    Therefore, the LIF does not contain any edges that are blocked.
    """

    edge_id: str
    """
    Unique identifier of the edge across all layouts within this LIF file.

    Different LIF files, especially from different vehicle
    integrators, may contain duplicate edgeIds. In this
    case, it is the responsibility of the (third-party)
    master control system to track whichever internal
    unique edgeId it wishes to use, and to map this to
    a vehicle integrator‘s edgeId for its specific LIF.
    """

    start_node_id: str
    """
    Id of the start node.
    
    The start node must always be part of the current layout.
    """

    end_node_id: str
    """
    Id of the end node.
    
    The end node can be located in another layout.
    This models a transition from one layout to another.
    """

    vehicle_type_edge_properties: list[VehicleTypeEdgeProperties]
    """
    Vehicle type specific properties for this edge.

    This attribute must not be empty. For each allowed vehicle type there must be an element.
    """

    edge_name: str | None = None
    """
    Name of the edge.
    
    This should only be for visualization purposes. 
    This attribute must not be used for any kind of identification or other logical purpose.
    """

    edge_description: str | None = None
    """
    Brief description of the edge. 
    
    This should only be used for visualization or diagnostic purposes.
    """

    # integrity is checked in __post_init__ because this is run automatically, no matter whether the object is
    # created by reading from a camel dict or by constructing one manually.
    def __post_init__(self):
        if len(self.vehicle_type_edge_properties) == 0:
            raise ValueError("Edge.vehicle_type_edge_properties must not be empty")

    def get_properties_for_vehicle_type(self, vehicle_type_id: str) -> VehicleTypeEdgeProperties | None:
        """
        Get the properties for a specific vehicle type.

        :param vehicle_type_id: The vehicle type id.
        :return: The properties for the vehicle type, or None if not found.
        """
        for properties in self.vehicle_type_edge_properties:
            if properties.vehicle_type_id == vehicle_type_id:
                return properties
        return None
