from abc import ABC, abstractmethod

from auto_all import public

from generalized_path_finding.model.path import Path


@public
class PathFinder[V](ABC):
    """
    Implementers of PathFinder are shortest path algorithms.

    An instance of PathFinder must hold all data needed to calculate shortest paths, including a graph most likely.
    """

    @abstractmethod
    def find_shortest_path(self, source: V, destination: V) -> Path[V] | None:
        """
        Compute the shortest path between nodes a and b.

        Shortest as in the sum of edge weights used is minimal.
        The edge weight is defined by the data provided to the PathFinder and is not limited to "distance".

        Returns None if there is no such path, i.e. if a and b are not connected.

        :param source: The start node.
        :param destination: The end node.
        """
        pass
