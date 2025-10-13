from dataclasses import dataclass
from typing import Optional

from auto_all import public


@public
@dataclass
class Node:
    name: str
    """
    Unique identifier of the Node.
    """

    x_meter: float
    """
    X coordinate of the physical Node in meters.
    """

    y_meter: float
    """
    Y coordinate of the physical Node in meters.
    """

    z_meter: float
    """
    Z coordinate of the physical Node in meters.
    """

    X: Optional[int] = None
    """
    X coordinate of the Node in visualization in pixels.

    """
    Y: Optional[int] = None
    """
    Y coordinate of the Node in visualization in pixels.
    """

    network: Optional[str] = None
    """
    Identifier of the network this Node resides in.

    This is usually a floor identifier.
    """

    # the rest of the fields is just for visualizations
