from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ChData:
    """
    Represents data related to a contraction hierarchy (CH) file.
    """

    ch_file: str
    """
    Path to a file containing the contraction hierarchy of the graph in the format by RoutingKit.
    """

    edge_list: List[Tuple[int, int, int]]
    """
    Edge list of the graph encoded in the ContractionHierarchy.
    Each edge is a tuple (source, target, weight). 
    """
    # Needed, because the ContractionHierarchy does not contain the original graph anymore and the order of the edge
    #     list is important because RoutingKit only outputs indices into the edge list the ContractionHierarchy was
    #     built with. Also, this format is independent of any previous format (like networkx or similar)

    number_of_nodes: int
    """
    Number of nodes in the graph.
    """
    # Needed, because this cannot necessarily be implied from the edge_list.