from auto_all import start_all, end_all

start_all()
from .lif import LifDataProvider
from .mfn_excel import MfnDataProvider
from .osm import OsmDataProvider

end_all()
