from abc import ABC, abstractmethod

from auto_all import public

from generalized_path_finding.model.ch_data import ChData
from generalized_path_finding.model.networkx_data import NetworkxData
from generalized_path_finding.model.osm_ch_data import OsmChData
from generalized_path_finding.nodes import GeoCoords


@public
class DataProvider[V](ABC):
    @abstractmethod
    def number_of_nodes(self) -> int:
        pass


@public
class NetworkxDataProvider[V](DataProvider[V]):
    """
    Marks a DataProvider that supports providing data in the NetworkX intermediate format.
    """

    @abstractmethod
    def get_networkx_data(self) -> "NetworkxData[V]":
        """
        Convert the data into the NetworkX intermediate format and return it.

        :return: data in the NetworkX intermediate format.
        """
        pass  # pragma: no cover

    def number_of_nodes(self) -> int:
        return self.get_networkx_data().graph.number_of_nodes()


@public
class ChDataProvider(DataProvider[int]):
    """
    Marks a DataProvider that supports providing data in the ContractionHierarchy intermediate format.
    """

    @abstractmethod
    def get_ch_data(self) -> "ChData":
        """
        Convert the data into the ContractionHierarchy intermadiate format and return it.

        :return: data in the ContractionHierarchy intermediate format.
        """
        pass  # pragma: no cover

    def number_of_nodes(self) -> int:
        return self.get_ch_data().number_of_nodes


@public
class OsmChDataProvider(DataProvider[GeoCoords]):
    """
    Marks a DataProvider that supports providing data in the OSM .graph and ContractionHierarchy intermediate format.
    """

    @abstractmethod
    def get_osm_ch_data(self) -> "OsmChData":
        """
        Convert the data into the OSM .graph and ContractionHierarchy intermadiate format and return it.

        :return: data in the OSM .graph and ContractionHierarchy intermediate format.
        """
        pass  # pragma: no cover

    def number_of_nodes(self) -> int:
        raise NotImplementedError  # FEATURE: implement (not necessary in current system)
