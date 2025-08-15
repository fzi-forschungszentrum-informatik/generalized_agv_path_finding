from dataclasses import dataclass


@dataclass
class OsmChData:
    """
    Represents data related to contraction hierarchy (CH) files and graph files.

    This class is used to store and access information regarding a graph and the
    related contraction hierarchy file.
    """

    graph_file: str
    """
    Path to the graph file containing data about the OSM graph in the format by PyRoutingKit.
    """

    ch_file: str
    """
    Path to the contraction hierarchy file in the format by RoutingKit.
    """