"""
All object types specified in the Layout Interchange Format (LIF) using dataclasses.

All classes support deserialization from and serialization to dicts that can be used with `json` to read and write
LIF files.

Specification of LIF 1.0.0:
https://vdma.org/documents/34570/3317035/FuI_Guideline_LIF_GB.pdf/779bc75c-9525-8d13-412e-fff82bc6ab39?t=1710513623026

All data models and documentation is taken from there.
"""
from auto_all import start_all, end_all

from .action import *
from .edge import *
from .layout import *
from .metainformation import *
from .node import *
from .station import *
from .trajectory import *

start_all()
from .lif import LIF
from .lif_data_provider import LifDataProvider

end_all()
