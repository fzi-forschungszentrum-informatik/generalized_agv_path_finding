from dataclasses import dataclass

from auto_all import public

from .camelserial import CamelSerial
from .edge import Edge
from .node import Node
from .station import Station


@public
@dataclass
class Layout(CamelSerial):
    """
    A layout for order generation and routing.

    This layout holds relevant information independently of possible vehicles or (third-party) master control systems.
    It is intended to hold the information for all different vehicle types.

    Nodes and edges formats a graph structure that is used as foundation for order generation and routing.

    A layout holds information that can be topologically considered a "plane",
    i.e., multiple levels must be modelled in different layouts.

    It is also possible to partition the facility into multiple layouts even if the encoded information can be
    considered to lie on the same level. Each layout has the same origin of coordinates.
    """

    layout_id: str
    """
    Unique identifier for this layout.
    """

    nodes: list[Node]
    """
    Collection of all nodes in the layout.
    """

    edges: list[Edge]
    """
    Collection of all edges in the layout.
    """

    # In the specification, this is not optional, but the same document contains examples omitting it.
    stations: list[Station] | None = None
    """
    Collection of all stations in the layout.
    """

    layout_name: str | None = None
    """
    Human-readable name of the layout (e.g., for displaying).
    """

    layout_version: str | None = None
    """
    Version of the layout.
    
    It is suggested that this be an integer, represented as a string, incremented with each change, starting at „1“.
    """

    layout_level_id: str | None = None
    """
    This attribute can be used to explicitly indicate which level or floor within a building or buildings a layout 
    represents in a situation where there are multiple, such as multiple levels in the same facility, 
    or two disconnected areas in the same facility.
    """

    layout_description: str | None = None
    """
    Brief description of the layout.
    """
