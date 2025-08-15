import os
import pathlib
import tempfile

import networkx as nx
import pytest

from generalized_path_finding.algorithms.nx_routing_kit import NxRoutingKit
from generalized_path_finding.model import Path
from generalized_path_finding.model.networkx_data import NetworkxData
from tests.util import remove_cache_file_if_coverage

current_path = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))


def local_path(relative_path):
    return str(current_path / relative_path)


def make_path_finder():
    # Demo graph: nodes 0-5, edges with weights
    # 0 --2--> 1 --9--> 2 --5--> 5
    #  \               /
    #   3             4
    #    \           /
    #     3 ---1--> 4
    # There are two main paths from 0 to 5: 0-1-2-5 and 0-3-4-2-5, the latter is shorter
    graph = nx.MultiDiGraph([
        (0, 1, "0 -> 1", {"weight": 2}),
        (1, 2, "1 -> 2", {"weight": 9}),
        (2, "5", '2 -> "5"', {"weight": 5}),
        (0, 3, "0 -> 3", {"weight": 3}),
        (3, 4, "3 -> 4", {"weight": 1}),
        (4, 2, "4 -> 2", {"weight": 4}),
    ])
    nx_data: NetworkxData[int | str] = NetworkxData(graph, lambda _a, _b: 0)
    path_finder = NxRoutingKit(nx_data)
    return path_finder


def test_conversion():
    remove_cache_file_if_coverage(pathlib.Path(tempfile.gettempdir()) / "nx.acc74240.ch")
    _path_finder = make_path_finder()
    assert os.path.exists(pathlib.Path(tempfile.gettempdir()) / "nx.acc74240.ch")


def test_nx_routing_kit():
    path_finder = make_path_finder()
    path = path_finder.find_shortest_path(0, "5")

    assert path == Path(nodes=[0, 3, 4, 2, '5'], edges=['0 -> 3', '3 -> 4', '4 -> 2', '2 -> "5"'], cost=13)


def test_node_out_of_bounds():
    path_finder = make_path_finder()

    with pytest.raises(ValueError):
        path_finder.find_shortest_path(0, 7)

    with pytest.raises(ValueError):
        path_finder.find_shortest_path(7, 5)


def test_nx_routing_kit_with_multigraph():
    # same demo graph as in make_path_finder, but with a few multi edges added
    graph = nx.MultiDiGraph([
        (0, 1, "0 -> 1", {"weight": 2}),
        (1, 2, "1 -> 2", {"weight": 9}),
        (1, 2, "1 -> 2 (alt)", {"weight": 42}),  # multi edge (not used)
        (2, "5", '2 -> "5"', {"weight": 5}),
        (2, "5", '2 -> "5" (alt)', {"weight": 4}),  # multi edge (cheaper)
        (0, 3, "0 -> 3", {"weight": 3}),
        (3, 4, "3 -> 4", {"weight": 1}),
        (4, 2, "4 -> 2", {"weight": 4}),
    ])
    nx_data: NetworkxData[int | str] = NetworkxData(graph, lambda _a, _b: 0)
    path_finder = NxRoutingKit(nx_data)

    path = path_finder.find_shortest_path(0, "5")
    assert path == Path(nodes=[0, 3, 4, 2, '5'], edges=['0 -> 3', '3 -> 4', '4 -> 2', '2 -> "5" (alt)'], cost=12)
