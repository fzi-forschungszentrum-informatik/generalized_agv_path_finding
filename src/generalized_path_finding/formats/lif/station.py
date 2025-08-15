from dataclasses import dataclass

from auto_all import public

from .camelserial import CamelSerial


@public
@dataclass
class StationPosition(CamelSerial):
    """
    Centre point and orientation of a station.

    Only for visualization purposes
    """

    x: float
    """
    X position of the station in the layout in reference to the global origin in meters.
    """

    y: float
    """
    Y position of the station in the layout in reference to the global origin in meters.
    """

    theta: float | None = None
    """
    Absolute orientation of the station on the node
    
    Range: [-Pi ... Pi]
    """


@public
@dataclass
class Station(CamelSerial):
    """
    Every point where a vehicle can explicitly interact with the environment, including but not limited to physical
    interactions.
    """

    station_id: str
    """
    Unique identifier of the station across all layouts within this LIF file.

    It is recommended that stationIds match and align between all LIFs from all vehicle integrators and other load 
    handling systems such as WMSs, as well as physical visual labelling and the like.
    """

    interaction_node_ids: list[str]
    """
    List of nodeIds for this station.
    
    These are the nodes that represent the position at which interaction with this station takes place. Multiple 
    nodes can be listed for stations which can be accessed in multiple ways (such as stations that can be approached 
    from multiple directions, e.g.: a station which can receive a EUR pallet longitudinally or laterally). 
    
    This attribute must not be empty; there must be at least one nodeId.
    
    The decision of which nodeId is used is the responsibility of the (third-party) master control system. Choosing 
    the correct interaction node may require that the (third-party) master control system considers the list of load 
    sets defined on the edge or edges leading to the interaction node.
    """

    station_name: str | None = None
    """
    Human-readable name for the station (e.g., for displaying).
    """

    station_description: str | None = None
    """
    Brief description of the station.
    """

    station_height: float = 0
    """
    Absolute physical height of the station in meters.
    
    Range: [0 ... float64.max]
    
    If not defined, the station height is 0.
    """

    station_position: StationPosition | None = None
    """
    Centre point and orientation of the station.
    
    Only for visualization purposes.
    """

    # integrity is checked in __post_init__ because this is run automatically, no matter whether the object is
    # created by reading from a camel dict or by constructing one manually.
    def __post_init__(self):
        if len(self.interaction_node_ids) == 0:
            raise ValueError("Station.interaction_node_ids must not be empty")
