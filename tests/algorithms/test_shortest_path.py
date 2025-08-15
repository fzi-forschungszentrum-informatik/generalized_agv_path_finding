import math

import networkx as nx

from generalized_path_finding.model.path import shortest_path_from_node_list


def test_shortest_path_from_node_list():
    # multi graph
    graph = nx.MultiDiGraph()
    graph.add_edge(0, 1, key="E0", weight=5.5)
    graph.add_edge(0, 1, key="E1", weight=2.0)
    graph.add_edge(1, 2, key="E2", weight=1.0)
    graph.add_edge(0, 2, key="E3", weight=100)

    path = shortest_path_from_node_list([0, 1, 2], graph, "weight")

    assert path.nodes == [0, 1, 2]
    assert path.edges == ["E1", "E2"]
    assert math.isclose(path.cost, 3.0)
