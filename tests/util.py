import os
import pathlib
from dataclasses import dataclass

import networkx as nx

from generalized_path_finding.model.data_provider import NetworkxDataProvider, ChDataProvider
from generalized_path_finding.model.networkx_data import NetworkxData
from generalized_path_finding.model.osm_ch_data import OsmChData


def print_graph(graph):
    print()
    print(graph)
    # graph of undirected version
    undirected_graph = graph.to_undirected()
    nx.write_network_text(undirected_graph)
    print("nodes:", [graph.nodes[node] for node in graph.nodes])
    print("edges:", [graph.edges[edge] for edge in graph.edges])


@dataclass
class DummyNetworkxDataProvider[V](NetworkxDataProvider[V]):
    data: NetworkxData[V]

    def get_networkx_data(self) -> NetworkxData[V]:
        return self.data


@dataclass
class DummyChDataProvider(ChDataProvider):
    data: OsmChData

    def get_ch_data(self) -> OsmChData:
        return self.data


def is_coverage():
    import coverage

    cov = coverage.Coverage.current()
    return cov is not None and cov._started


def remove_cache_file_if_coverage(cache_file: pathlib.Path | str):
    if is_coverage() and os.path.exists(cache_file):
        os.remove(cache_file)
