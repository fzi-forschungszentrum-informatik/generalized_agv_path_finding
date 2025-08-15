# TODO: check standards for publishable packages

from auto_all import start_all, end_all
from beartype import BeartypeConf
from beartype.claw import beartype_this_package

beartype_this_package(conf=BeartypeConf(is_pep484_tower=True))

start_all()
from .model import Path, PathFinder
from .formats import LifDataProvider, MfnDataProvider, OsmDataProvider
from .algorithms import AStar, RoutingKit, NxRoutingKit, OsmRoutingKit
from .helper import create_path_finder, Algorithm

end_all()
