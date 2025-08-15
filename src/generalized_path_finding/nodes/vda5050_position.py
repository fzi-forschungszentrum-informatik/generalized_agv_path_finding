import math
from dataclasses import dataclass

from auto_all import public


@public
@dataclass(frozen=True)
class VDA5050Position:
    """
    A node position as by the `VDA5050 specification
    <https://github.com/VDA5050/VDA5050/blob/main/VDA5050_EN.md#666-implementation-of-the-order-message>` but limited
    to vehicle-independent values.

    This omits the optional allowed deviation attributes as well as theta, as they are irrelevant to distances.
    """

    x: float
    """
    The x coordinate of the position.
    """

    y: float
    """
    The y coordinate of the position.
    """

    map_id: str
    """
    The map this node is located in.
    """

    @staticmethod
    def euclidean_distance(pos_a: "VDA5050Position", pos_b: "VDA5050Position") -> float:
        """
        Only computes the 2d Euclidean distance between two positions. The mapIds of the vda5050 positions are ignored.
        """
        return math.hypot(pos_a.x - pos_b.x, pos_a.y - pos_b.y)
