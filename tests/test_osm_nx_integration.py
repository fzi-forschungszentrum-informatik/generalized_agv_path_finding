import os
import pathlib
import random

import matplotlib.pyplot as plt
from pyrosm import OSM

from generalized_path_finding import OsmDataProvider, AStar, OsmRoutingKit
from tests.constants import EXACT_ORIGIN, EXACT_DESTINATION
from tests.util import print_graph

current_path = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))


def local_path(relative_path):
    return str(current_path / relative_path)


def random_walk_subgraph(G, target_nodes=10):
    start = random.choice(list(G.nodes()))
    walk = [start]
    while len(set(walk)) < target_nodes:
        curr = walk[-1]
        neighbors = list(G.neighbors(curr))
        if not neighbors:
            # restart if stuck
            curr = random.choice(list(G.nodes()))
            walk.append(curr)
        else:
            walk.append(random.choice(neighbors))
    nodes = list(dict.fromkeys(walk))[:target_nodes]  # preserve order
    return G.subgraph(nodes).copy()


def show_paths(a_star_path, routing_kit_path):
    # Create a map centered on the first point of a_star_path
    m = plt.figure(figsize=(10, 10))
    ax = m.add_subplot(111)

    # Plot A* path in blue
    astar_lats = [node.lat for node in a_star_path.nodes]
    astar_lons = [node.lon for node in a_star_path.nodes]
    ax.plot(astar_lons, astar_lats, 'b-', linewidth=2, alpha=0.8, label='A* Path')

    # Plot RoutingKit path in red
    rk_lats = [node.lat for node in routing_kit_path.nodes]
    rk_lons = [node.lon for node in routing_kit_path.nodes]
    ax.plot(rk_lons, rk_lats, 'r-', linewidth=2, alpha=0.8, label='RoutingKit Path')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.legend()

    # Save the map
    plt.show()


def test_manual_osm_to_nx_conversion():
    print("loading...")
    osm = OSM(local_path("formats/osm/andorra-latest.osm.pbf"))
    nodes, edges = osm.get_network(nodes=True, network_type="driving")
    G = osm.to_graph(nodes, edges, graph_type="networkx", retain_all=True)

    print(G.number_of_nodes(), G.number_of_edges())
    print(list(G.nodes)[:10])
    print(list(G.edges)[:10])

    print("sampling...")
    sample = random_walk_subgraph(G)
    print_graph(sample)


def test_osm_astar_returns_same_path_as_routing_kit():
    data_provider = OsmDataProvider(local_path("formats/osm/andorra-latest.osm.pbf"))
    nx_data = data_provider.get_networkx_data()
    a_star = AStar(nx_data)

    # when using AStar with OSM data, nodes are identified by their *exact* GeoCoordinates
    a_star_path = a_star.find_shortest_path(EXACT_ORIGIN, EXACT_DESTINATION)

    routing_kit = OsmRoutingKit(data_provider.get_osm_ch_data())
    routing_kit_path = routing_kit.find_shortest_path(EXACT_ORIGIN, EXACT_DESTINATION)

    # show_paths(a_star_path, routing_kit_path)

    assert a_star_path.nodes == routing_kit_path.nodes
    print(f"{a_star_path.cost = }, {routing_kit_path.cost = }")
    # even though they find the same path, the time cost is different due to different speed limits.
