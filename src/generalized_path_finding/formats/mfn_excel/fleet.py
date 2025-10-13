from dataclasses import dataclass
from auto_all import public

@public
@dataclass
class Fleet:
    """
    A fleet consists of a name and an average speed.
    """

    name: str
    """
    The name of the fleet used e.g. for the paths or connections.
    """

    avg_speed_mps: float
    """
    The average speed of the fleet in meters per second.
    """