import os
import pathlib

import pytest

from generalized_path_finding.algorithms import RoutingKit
from generalized_path_finding.formats.osm.osm_data_provider import OsmDataProvider
from generalized_path_finding.model.ch_data import ChData

current_path = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
def local_path(relative_path):
    return str(current_path / relative_path)

def test_invalid_path():
    ch_data = ChData("", [], 3)
    with pytest.raises(RuntimeError, match="open"):
        RoutingKit(ch_data)



@pytest.mark.run(after="test_distance_vs_duration")
def test_node_out_of_bounds():
    data_provider = OsmDataProvider(local_path("../formats/osm/andorra-latest.osm.pbf"))
    osm_data = data_provider.get_osm_ch_data()

    # only the number of nodes is important for this test case
    ch_data = ChData(osm_data.ch_file, [], 3)
    path_finder = RoutingKit(ch_data)

    with pytest.raises(ValueError):
        path_finder.find_shortest_path(0, 7)

    with pytest.raises(ValueError):
        path_finder.find_shortest_path(7, 5)
