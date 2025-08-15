import networkx as nx

from generalized_path_finding.algorithms import AStar
from generalized_path_finding.model.networkx_data import NetworkxData


def test_without_heuristic():
    graph = nx.MultiDiGraph()
    graph.add_edge(0, 1, key="E1", weight=1.0)
    graph.add_edge(1, 2, key="E2", weight=2.0)
    data = NetworkxData(graph, lambda u, v: 0.0)
    path_finder = AStar(data)
    path = path_finder.find_shortest_path(0, 2)
    assert path.nodes == [0, 1, 2]


def test_with_heuristic():
    graph = nx.MultiDiGraph()
    graph.add_edge(0, 1, key="E1", weight=1.0)
    graph.add_edge(1, 2, key="E2", weight=2.0)
    data = NetworkxData(graph, lambda u, v: 0.0)
    path_finder = AStar(data)
    path = path_finder.find_shortest_path(0, 2)
    assert path.nodes == [0, 1, 2]


def test_without_heuristic_and_no_path():
    graph = nx.MultiDiGraph()
    graph.add_edge(0, 1, key="E1", weight=1.0)
    graph.add_edge(3, 2, key="E2", weight=2.0)
    data = NetworkxData(graph, lambda u, v: 0.0)
    path_finder = AStar(data)
    path = path_finder.find_shortest_path(0, 2)
    assert path is None


def test_with_heuristic_and_no_path():
    graph = nx.MultiDiGraph()
    graph.add_edge(0, 1, key="E1", weight=1.0)
    graph.add_edge(3, 2, key="E2", weight=2.0)
    data = NetworkxData(graph, lambda u, v: 0.0)
    path_finder = AStar(data)
    path = path_finder.find_shortest_path(0, 2)
    assert path is None
