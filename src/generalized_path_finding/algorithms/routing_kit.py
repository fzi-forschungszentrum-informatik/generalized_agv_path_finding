from typing import Tuple

from auto_all import public
from pyroutingkit import load_contraction_hierarchy, query_contraction_hierarchy_path

from generalized_path_finding.model.ch_data import ChData
from generalized_path_finding.model.path import Path
from generalized_path_finding.model.pathfinder import PathFinder

INF_WEIGHT = 2147483647
"""Used by RoutingKit to indicate that there is no path between two nodes."""
# see https://github.com/RoutingKit/RoutingKit/blob/master/include/routingkit/constants.h#L7


@public
class RoutingKit(PathFinder[int]):
    def __init__(self, data: ChData):
        """
        A PathFinder to find shortest paths using the RoutingKit ContractionHierarchy algorithm given a
        ContractionHierarchy and its generating edge list.

        :param data: The ContractionHierarchy and its generating edge list.
        """

        self.data = data
        self.ch_ptr = load_contraction_hierarchy(self.data.ch_file)
        # FEATURE: test if the use of std::shared_ptr really prevents memory leaks (by tracking memory usage as the ch_ptr
        #  object is garbage collected) https://pybind11.readthedocs.io/en/stable/advanced/smart_ptrs.html

    # RoutingKit only uses integers as weights
    def find_shortest_path(self, source: int, target: int) -> Path[int, Tuple[int, int, int]] | None:
        if not source in range(self.data.number_of_nodes):
            raise ValueError(f"Invalid node index: source={source} not in [0, {self.data.number_of_nodes})")
        if not target in range(self.data.number_of_nodes):
            raise ValueError(f"Invalid node index: target={target} not in [0, {self.data.number_of_nodes})")

        arcs, cost = query_contraction_hierarchy_path(self.ch_ptr, source, target)

        if cost == INF_WEIGHT:
            return None  # no path between source and destination

        # sanity check
        assert sum(self.data.edge_list[arc][2] for arc in arcs) == cost

        edges = [self.data.edge_list[arc] for arc in arcs]
        nodes = [self.data.edge_list[arc][0] for arc in arcs] + [self.data.edge_list[arcs[-1]][1]]

        return Path(nodes, edges, cost)
