import warnings
from dataclasses import dataclass

from auto_all import public

from .camelserial import CamelSerial
from .layout import Layout
from .metainformation import Metainformation


@public
@dataclass
class LIF(CamelSerial):
    """
    A complete description of the facility from the perspective of vehicle routing.
    """

    meta_information: Metainformation
    """
    Contains meta information.
    """
    layouts: list[Layout]
    """
    Collection of layouts used in the facility by the driverless transport system. 
    All layouts geometrically refer to the same project-specific global origin.
    """

    @staticmethod
    def _pre_deserialization_check(camel_dict: dict) -> bool:
        version = camel_dict["metaInformation"]["lifVersion"]
        if version != "1.0.0":
            warnings.warn(f"This implementation uses the LIF version 1.0.0, but reading a file using LIF version "
                          f"{version}")
        return True
