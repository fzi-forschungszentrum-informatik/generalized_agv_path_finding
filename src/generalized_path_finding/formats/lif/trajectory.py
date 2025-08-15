import math
from dataclasses import dataclass

import geomdl
from auto_all import public
from geomdl import BSpline

from .camelserial import CamelSerial


@public
@dataclass
class ControlPoint(CamelSerial):
    """
    Control point of a NURBS.
    """

    x: float
    """
    X position on the layout in reference to the global origin in meters.
    """
    # unit not given in spec

    y: float
    """
    Y position on the layout in reference to the global origin in meters.
    """
    # unit not given in spec

    weight: float | None = 1.0
    """
    The weight with which this control point pulls on the curve. 
    
    When not defined, the default is 1.0.

    Range: [0.0 ... float64.max]
    """


@public
@dataclass
class Trajectory(CamelSerial):
    """
    Trajectory for an edge as a NURBS.
    """

    knot_vector: list[float]
    """
    Sequence of parameter values that determines where and how the control points affect the NURBS curve.
    
    `knot_vector` has size of number of control points + degree + 1
    
    Range of items: [0.0 ... 1.0]
    """

    control_points: list[ControlPoint]
    """
    List of objects defining the control points of the NURBS, which includes the beginning and end points.
    """


    degree: int = 1
    """
    Defines the number of control points that influence any given point on the curve. 
    Increasing the degree increases continuity.
    
    If not defined, the default value is 1
    
    Range: [1.0 ... integer.max]
    """

    def approximate_length(self, num_samples: int = 10):
        """
        Calculate the approximate length of this trajectory.

        If `degree` is 1, the calculation is exact.
        Otherwise, `geomdl` is used to sample the NURBS curve and approximate the length.

        :param num_samples: Number of samples to take.
        More samples increases the accuracy of the calculation.
        Only applies when `degree` is greater than 1.
        """

        if self.degree == 1:
            # trajectory is polyline
            dist = 0.0
            # length is Euclidean distance between each pair of consecutive control points
            for i in range(len(self.control_points) - 1):
                dist += math.sqrt(
                    (self.control_points[i].x - self.control_points[i + 1].x) ** 2 +
                    (self.control_points[i].y - self.control_points[i + 1].y) ** 2
                )
            return dist
        else:
            curve = BSpline.Curve()
            curve.degree = self.degree
            curve.ctrlpts = [[p.x, p.y] for p in self.control_points]
            curve.knotvector = self.knot_vector
            curve.sample_size = num_samples
            curve.evaluate()
            return geomdl.operations.length_curve(curve)
