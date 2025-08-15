from dataclasses import dataclass
from enum import Enum
from typing import Type, Tuple, List

from auto_all import public

from generalized_path_finding.algorithms import AStar, OsmRoutingKit, NxRoutingKit
from generalized_path_finding.algorithms import RoutingKit
from generalized_path_finding.model import OsmChData, NetworkxData, ChData
from generalized_path_finding.model.data_provider import NetworkxDataProvider, ChDataProvider, DataProvider, \
    OsmChDataProvider
from generalized_path_finding.model.pathfinder import PathFinder


@public
class Algorithm(Enum):
    A_STAR = "a_star"
    ROUTING_KIT = "osm_routing_kit"
    AUTO = "auto"


@dataclass
class ChooseBySize():
    segments: List[Tuple[int, Type[PathFinder]]]
    """
    (threshold, algorithm) pairs.
    If the number of nodes in the network is the threshold or more, use the specified algorithm.
    Sorted ascending by number of nodes.
    """

    def select(self, number_of_nodes: int) -> Type[PathFinder]:
        for threshold, algorithm in self.segments[::-1]:
            if number_of_nodes >= threshold:
                return algorithm
        raise Exception(f"no algorithm found for {number_of_nodes} nodes")


InternalDataFormat = NetworkxData | OsmChData | ChData
DATA_FORMAT_PROVIDER = {
    OsmChData: OsmChDataProvider,
    ChData: ChDataProvider,
    NetworkxData: NetworkxDataProvider,
}
DATA_EXTRACTOR_METHOD = {
    OsmChDataProvider: "get_osm_ch_data",
    ChDataProvider: "get_ch_data",
    NetworkxDataProvider: "get_networkx_data",
}

PREFERRED_DATA_FORMATS_PER_ALGORITHM: dict[Type[PathFinder], list[Type[InternalDataFormat]]] = {
    AStar: [NetworkxData],
    OsmRoutingKit: [OsmChData],
    RoutingKit: [ChData],
    NxRoutingKit: [NetworkxData],
}

DECISION_TREE: dict[Algorithm, dict[Type[DataProvider], Type[PathFinder] | ChooseBySize]] = {
    Algorithm.A_STAR: {
        OsmChDataProvider: AStar,
        NetworkxDataProvider: AStar,
    },
    Algorithm.ROUTING_KIT: {
        OsmChDataProvider: OsmRoutingKit,
        ChDataProvider: RoutingKit,
        NetworkxDataProvider: NxRoutingKit,
    },
    Algorithm.AUTO: {
        OsmChDataProvider: OsmRoutingKit,
        ChDataProvider: RoutingKit,
        NetworkxDataProvider: ChooseBySize([(0, AStar), (10_000, NxRoutingKit)]),
    }
}
"""
Maps algorithm types and DataProviders to a suitable algorithm class and a list of data formats supported by the
algorithm, in order of preference from most to least preferred.
This is used to determine which data provider to use for a given algorithm.
"""


def _choose_algorithm_class(data_provider: DataProvider, algorithm: Algorithm):
    prefs = DECISION_TREE[algorithm]
    for dp_type in prefs:
        if isinstance(data_provider, dp_type):
            algo = prefs[dp_type]
            if isinstance(algo, ChooseBySize):
                return algo.select(data_provider.number_of_nodes())
            else:
                return algo
    raise Exception(f"algorithm {algorithm} not compatible with data provider {data_provider}")


@public
def create_path_finder[V](data_provider: DataProvider[V], algorithm: Algorithm = Algorithm.AUTO, *args, **kwargs) -> \
        PathFinder[V]:
    """
    Establishes a connection between a specified data provider and type of algorithm, selecting the
    appropriate data from the provider and the appropiate implementation of the algorithm based on compatibility.
    This function determines the internal data format required by the algorithm and initializes the algorithm with
    the relevant data.

    :param data_provider: The source of the data, supporting at least one internal data format.
    :param algorithm: The type of algorithm to be initialized using the data provider.
    :param args: Additional arguments passed to the algorithm class during initialization.
    :param kwargs: Additional keyword arguments passed to the algorithm class during initialization.
    :return: A PathFinder initialized with the data provided by the data provider.
    """

    algo_class = _choose_algorithm_class(data_provider, algorithm)
    for data_format in PREFERRED_DATA_FORMATS_PER_ALGORITHM[algo_class]:
        dp_type = DATA_FORMAT_PROVIDER[data_format]
        if isinstance(data_provider, dp_type):
            data = getattr(data_provider, DATA_EXTRACTOR_METHOD[dp_type])()
            break
    else:
        assert False, (f"selected algorithm {algo_class} does not support data provider {data_provider}, should have "
                       f"been caught in _choose_algorithm_class()")

    # noinspection PyArgumentList
    return algo_class(data, *args, **kwargs)
