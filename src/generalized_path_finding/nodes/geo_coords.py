from dataclasses import dataclass

from auto_all import public
from geopy.distance import geodesic


@public
@dataclass(frozen=True)
class GeoCoords:
    """
    A point on earth, represented by latitude and longitude.
    """

    lat: float
    """
    Latitude in degrees [-90, +90]
    """

    lon: float
    """
    Longitude in degrees [-180, +180]
    """

    def distance_to(self, other: "GeoCoords") -> float:
        return geodesic((self.lat, self.lon), (other.lat, other.lon)).meters
