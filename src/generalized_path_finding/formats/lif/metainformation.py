from dataclasses import dataclass

from auto_all import public

from .camelserial import CamelSerial


@public
@dataclass
class Metainformation(CamelSerial):
    """
    Contains meta information.
    """

    project_identification: str
    """
    Human-readable name of the project (e.g., for display purposes).
    """

    creator: str
    """
    Creator of the LIF file (e.g., name of company, or name of person).
    """

    export_timestamp: str
    """
    The timestamp at which this LIF file was created/updated/modified. 
    Used to distinguish LIF file versions over time.
    
    Timestamp format is ISO8601 in UTC (YYYY-MM-DDTHH:mm:ss.ssZ, e.g., "2017-04-15T11:40:03.12Z").
    """

    lif_version: str
    """
    Version of LIF: [Major].[Minor].[Patch] (1.0.0).
    """
