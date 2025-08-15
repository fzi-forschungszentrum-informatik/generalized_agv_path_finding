import os
import pathlib

from generalized_path_finding.algorithms import NxRoutingKit
from generalized_path_finding.formats.lif import LifDataProvider

current_path = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))


def local_path(relative_path):
    return str(current_path / relative_path)


def test_lif_astar_with_distance():
    file = current_path / "formats/lif/LIF_4_4_MAPF.json"
    dp = LifDataProvider(file)
    rk = NxRoutingKit(dp.get_networkx_data(), original_file=file)

    p = rk.find_shortest_path("N_0_2", "N_3_3")
    assert p is not None
    assert p.cost == 4
    assert p.nodes == ['N_0_2', 'N_1_2', 'N_2_2', 'N_3_2', 'N_3_3']
    assert p.edges == ['E-0_2-1_2', 'E-1_2-2_2', 'E-2_2-3_2', 'E-3_2-3_3']

    p = rk.find_shortest_path("N_0_2", "N_1_3")
    assert p is not None
    assert p.cost == 2
    assert p.nodes[0] == 'N_0_2' and p.nodes[-1] == 'N_1_3'
    # path is ambiguous

    p = rk.find_shortest_path("N_3_0", "N_2_2")
    assert p is None
