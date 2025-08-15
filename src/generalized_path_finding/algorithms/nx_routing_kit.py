import pathlib

from auto_all import public

from generalized_path_finding.algorithms import RoutingKit
from generalized_path_finding.model import PathFinder, Path
from generalized_path_finding.model.networkx_data import NetworkxData, DEFAULT_SCALING_FACTOR


@public
class NxRoutingKit[V](PathFinder[V]):
    def __init__(
            self,
            nx_data: NetworkxData[V],
            scaling_factor: int = DEFAULT_SCALING_FACTOR,
            original_file: str | pathlib.Path | None = None,
            cache_dir: str | pathlib.Path | None = None
    ):
        """
        A PathFinder to find shortest paths using the RoutingKit ContractionHierarchy algorithm on the NetworkX
        intermediate format.

        Rounds the edge weights to the precision of scaling_factor^-1 before passing them to RoutingKit as integers.

        :param nx_data: the graph and heuristic (not used) in the NetworkX intermediate format.
        :param scaling_factor: the precision of the edge weights in the NetworkX intermediate format. Defaults to 1e6.
        :param original_file: the original file used to create the NetworkX intermediate format. Used to name cache files.
        :param cache_dir: the directory to use for caching. Defaults to the operating systems temporary directory.
        """

        self.nx_data = nx_data
        self.scaling_factor = scaling_factor

        self.ch_data, self.mapping = nx_data.to_ch_data(self.scaling_factor, original_file, cache_dir)
        self.inverse_mapping = list(self.mapping.keys())

        self.routing_kit = RoutingKit(self.ch_data)

    def find_shortest_path(self, source: V, destination: V) -> Path[int, tuple[int, int, int]] | None:
        if source not in self.mapping:
            raise ValueError(f"Invalid node index: source={source} not in {self.mapping.keys()}")
        if destination not in self.mapping:
            raise ValueError(f"Invalid node index: destination={destination} not in {self.mapping.keys()}")

        path = self.routing_kit.find_shortest_path(self.mapping[source], self.mapping[destination])
        if path is None: return None
        path.cost /= self.scaling_factor
        path.nodes = [self.inverse_mapping[node] for node in path.nodes]
        path.edges = [
            next(key for key, attr
                 in self.nx_data.graph[self.inverse_mapping[s]][self.inverse_mapping[t]].items()
                 if round(attr["weight"] * self.scaling_factor) == w)
            for s, t, w in path.edges
        ]
        return path
