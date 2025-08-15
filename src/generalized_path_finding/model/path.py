from dataclasses import dataclass

from auto_all import public


@public
@dataclass
class Path[V, E=str]:
    # edges are strings for now. edges can be computed from nodes using the graph and only choosing the cheapest edges
    """
    A path is a sequence of edges in a weighted multi-graph.

    A list of nodes and a total cost are always inferred by a list of edges, by accumulating all edge costs and
    concatenating edge all edge sources and the last target, respectively. They are provided as well,
    as many algorithms already return them anyway.
    """

    nodes: list[V]
    edges: list[E]
    cost: float

    # FEATURE: always return distance and duration?


def shortest_path_from_node_list[V](nodes: list[V], graph, weight_key) -> Path[V]:
    """
    Given the node list of a path, compute the edge list and the cost by using the cheapest edge between each pair of
    consecutive nodes.

    :param nodes: the list of nodes of the path
    :param graph: the graph to choose the edges from
    :param weight_key: the key in each edge's property dictionary to use to determine the cost
    :return: a fully populated [Path] object
    """

    edges = []
    cost = 0.0
    for i in range(len(nodes) - 1):
        u, v = nodes[i], nodes[i + 1]
        # Find the edge with the minimum weight between u and v
        uv_edges = graph.get_edge_data(u, v)
        edge_key = min(uv_edges.keys(), key=lambda e, uv=uv_edges: uv[e][weight_key])
        edges.append(edge_key)
        cost += uv_edges[edge_key][weight_key]

    return Path(nodes, edges, cost)
