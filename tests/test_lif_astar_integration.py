import math
import os
from pathlib import Path

import pytest

from generalized_path_finding.algorithms import AStar
from generalized_path_finding.formats.lif import LifDataProvider

current_path = Path(os.path.dirname(os.path.abspath(__file__)))


def test_lif_astar_with_distance():
    dp = LifDataProvider(current_path / "formats/lif/LIF_4_4_MAPF.json")
    astar = AStar(dp.get_networkx_data())

    p = astar.find_shortest_path("N_0_2", "N_3_3")
    assert p is not None
    assert p.cost == 4
    assert p.nodes == ['N_0_2', 'N_1_2', 'N_2_2', 'N_3_2', 'N_3_3']
    assert p.edges == ['E-0_2-1_2', 'E-1_2-2_2', 'E-2_2-3_2', 'E-3_2-3_3']

    p = astar.find_shortest_path("N_0_2", "N_1_3")
    assert p is not None
    assert p.cost == 2
    assert p.nodes[0] == 'N_0_2' and p.nodes[-1] == 'N_1_3'
    # path is ambiguous

    p = astar.find_shortest_path("N_3_0", "N_2_2")
    assert p is None


def test_lif_astar_with_time():
    dp = LifDataProvider(current_path / "formats/lif/LIF_4_4_MAPF_b.json", time_cost=True)
    with pytest.raises(ValueError):
        dp._get_graph()
        # because there are edges without speed limit and no vehicle_max_speed is specified

    dp = LifDataProvider(current_path / "formats/lif/LIF_4_4_MAPF_b.json", time_cost=True, vehicle_max_speed=5.0)
    astar = AStar(dp.get_networkx_data())

    assert dp._get_heuristic()("N_1_0", "N_3_3") == math.hypot(2, 3) / dp.vehicle_max_speed

    p = astar.find_shortest_path("N_1_0", "N_3_3")
    assert p.cost == 1 + 2 + 2 + 0.2
    assert p.nodes == ['N_1_0', 'N_1_2', 'N_2_2', 'N_3_2', 'N_3_3']
    assert p.edges == ['E-1_0-1_2', 'E-1_2-2_2', 'E-2_2-3_2', 'E-3_2-3_3']
