import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import networkx as nx
from pyroutingkit import build_contraction_hierarchy

from generalized_path_finding.model.ch_data import ChData

DEFAULT_SCALING_FACTOR = 1_000_000


@dataclass
class NetworkxData[V]:
    """
    Data in the NetworkX intermediate format, comprising a graph and a heuristic.
    """

    graph: nx.MultiDiGraph
    """
    NetworkX graph. Each edge has a float-valued attribute with the key ``"weight"``.
    """

    heuristic: Callable[[V, V], float]
    """
    A function that takes two nodes and returns float-valued a lower bound for the cost between them.
    
    Should have much faster runtime than finding the shortest path between the two nodes.
    """

    def to_ch_data(
            self,
            scaling_factor: int = DEFAULT_SCALING_FACTOR,
            original_file: str | Path | None = None,
            cache_dir: str | Path | None = None,
    ) -> tuple["ChData", dict[V, int]]:
        """
        Converts the NetworkX graph to a ChData object, caching the ContractionHierarchy in a .ch file.

        Edge weights are rounded to the nearest integer.

        :param scaling_factor: Multiplier for the edge weights to improve the precision of rounding. Defaults to 1e6.
        :param original_file: the original file used to create the NetworkX intermediate format. Used to name cache files.
        :param cache_dir: the directory to use for caching. Defaults to the operating systems temporary directory.

        :return: A ChData object equivalent to this NetworkxData.
        """

        # Convert MultiDiGraph to simple DiGraph by keeping only the least costly edge between each node pair
        simple_graph = nx.DiGraph()
        for u, v, w in self.graph.edges.data("weight"):
            w = round(w * scaling_factor)
            if simple_graph.has_edge(u, v):
                if w < simple_graph[u][v]["weight"]:
                    simple_graph[u][v]["weight"] = w
            else:
                simple_graph.add_edge(u, v, weight=w)

        # map from V to ints
        # the node list is guaranteed to be in insertion order -> no sorting needed
        mapping = {node: idx for idx, node in enumerate(simple_graph.nodes)}
        edges = sorted(
            list((mapping[s], mapping[t], w) for s, t, w in simple_graph.edges.data("weight")))

        # hash graph
        for node in simple_graph.nodes:
            simple_graph.nodes[node]['idx'] = mapping[node]
        graph_hash = nx.weisfeiler_lehman_graph_hash(simple_graph, node_attr="idx", edge_attr='weight', digest_size=4)

        # choose ch_file location
        if original_file is not None:
            original_file = Path(original_file)
            if cache_dir is None:
                cache_dir = original_file.parent
        if cache_dir is None:
            cache_dir = tempfile.gettempdir()
        cache_dir = Path(cache_dir)
        basename = original_file.name if original_file is not None else "nx"
        ch_file = cache_dir / f"{basename}.{graph_hash}.ch"

        # check for a cached file
        if os.path.isfile(ch_file):
            print(".ch already up-to-date")
        else:
            print(f"converting networkx graph{f" ({original_file})" if original_file is not None else ""} to .ch")
            build_contraction_hierarchy(simple_graph.number_of_nodes(), edges, str(ch_file))

        return ChData(str(ch_file), edges, simple_graph.number_of_nodes()), mapping
