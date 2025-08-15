import networkx as nx
from auto_all import public

from generalized_path_finding.model.networkx_data import NetworkxData
from generalized_path_finding.model.path import Path, shortest_path_from_node_list
from generalized_path_finding.model.pathfinder import PathFinder

WEIGHT_KEY = "weight"


@public
class AStar[V](PathFinder):
    def __init__(self, data: NetworkxData[V]):
        """
        A PathFinder to find shortest paths using the A* algorithm implement by NetworkX in a graph and using a
        heuristic using anything as node label.

        NetworkX's implementation of A* is more efficient than its dijkstra algorithm. That's why AStar also accepts
        inputs without meaningful heuristic and then runs A* with a 0-heuristic, which is equivalent to, but faster
        than Dijkstra. (see test_compare_to_dijkstra)

        :param data: the graph and heuristic in the NetworkX intermediate format.
        """

        self.data = data

    def find_shortest_path(self, source: V, destination: V) -> Path[V] | None:
        if source not in self.data.graph:
            raise ValueError(f"source={source} not in graph")
        if destination not in self.data.graph:
            raise ValueError(f"destination={destination} not in graph")

        try:
            nodes = nx.astar_path(self.data.graph, source, destination, heuristic=self.data.heuristic,
                                  weight=WEIGHT_KEY)
        except nx.NetworkXNoPath:
            return None
        return shortest_path_from_node_list(nodes, self.data.graph, WEIGHT_KEY)
