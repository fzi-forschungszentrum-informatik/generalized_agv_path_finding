from dataclasses import dataclass

from auto_all import public

from .fleet_list import parse_fleets_list


@public
@dataclass
class Connection:
    """
    In the terminology of a Multi Floor Network Excel Schema, a Connection is a unidirectional arc from one node to
    another node in another network (on another floor).
    This is most likely an elevator.
    """

    name: str
    """
    A unique identifier for the Connection.
    
    There might be multiple paths between the same pair of Nodes.
    """

    origin_node_name: str
    """
    The name of the origin/starting Node of the Connection.
    """

    destination_node_name: str
    """
    The name of the destination/target Node of the Connection.
    """

    cal_trans_duration_seconds: int
    """
    The time it takes to travers this Connection.
    """

    origin_controls: str | None

    origin_network: str
    """
    The identifier of the network the origin node resides in.
    """

    destination_network: str
    """
    The identifier of the network the destination node resides in.
    """

    description: str | None

    pedestrians: str | None
    """
    What kind of pedestrians also use this Connection.
    """

    fleets: str
    """
    A pipe ("|") separated list of identifiers of the types of vehicles that can travers this Connection.
    
    Identifiers of types do not start or end with white whitespace, so arbitrary whitespace is allowed around "|". 
    """

    orientation: str | None
    comment: str | None

    def __post_init__(self):
        self.fleet_list = parse_fleets_list(self.fleets)

    def supports_fleet(self, fleet: str) -> bool:
        return fleet.strip().lower() in self.fleet_list
