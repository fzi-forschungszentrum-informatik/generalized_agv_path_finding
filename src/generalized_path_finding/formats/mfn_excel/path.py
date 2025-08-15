from dataclasses import dataclass
from typing import Any

from auto_all import public

from .fleet_list import parse_fleets_list


@public
@dataclass
class Path:
    """
    In the terminology of a Multi Floor Network Excel Schema, a Path is a unidirectional arc from one node to another
    node in the same network (on the same floor).
    """

    name: str
    """
    A unique identifier for the Path.
    
    There might be multiple paths between the same pair of Nodes.
    """

    origin_node_name: str
    """
    The name of the origin/starting Node of the Path.
    """

    destination_node_name: str
    """
    The name of the destination/target Node of the Path.
    """

    network: str
    """
    Identifier of the network this Node resides in.
    
    This is usually a floor identifier.
    Both the origin node and the destination node must also be in the same network as this Path. 
    """

    origin_id: int | None
    """
    The index of the origin node of the Path.
    Redundant with origin_node_name.
    """

    dest_id: int | None
    """
    The index of the destination node of the Path.
    Redundant with destination_node_name.
    """

    prio: int | None
    """
    The priority of the Path (prefer lower priority in path finding).
    
    Low priority values indicate paths that should preferably be used rather than paths with higher priority values.
    1 indicates main paths.
    2 indicates paths that should be avoided.
    3 indicates paths that can only be accessed with explicit permission.
    """

    speed_limit_mps: float | None
    """
    The speedlimit of vehicles on this Path in meters per second.
    """

    description: str | None
    color: str | None
    controls: Any | None

    pedestrians: str | None
    """
    What kind of pedestrians also use this Path.
    """

    fleets: str
    """
    A pipe ("|") separated list of identifiers of the types of vehicles that can travers this Path.
    """

    def __post_init__(self):
        self.fleet_list = parse_fleets_list(self.fleets)

    def supports_fleet(self, fleet: str) -> bool:
        return fleet.strip().lower() in self.fleet_list
