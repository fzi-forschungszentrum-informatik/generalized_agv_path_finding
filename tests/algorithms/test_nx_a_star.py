import json
import math
import os
import time
from pathlib import Path

import networkx as nx

current_path = Path(os.path.dirname(os.path.realpath(__file__)))


def get_graphs(n, path):
    # read from disk if preset, else generate new graphs and write them to disk
    if os.path.exists(path):
        with open(path, 'r') as f:
            graphs = [nx.node_link_graph(json.loads(line), edges="edges") for line in f]
    else:
        radius = 2 / math.sqrt(n)
        graphs = [nx.random_geometric_graph(n, radius) for _ in range(10)]
        with open(path, 'w') as f:
            for graph in graphs:
                json.dump(nx.node_link_data(graph, link="edges"), f)
                f.write('\n')  # Separate graphs with newlines

    return graphs


def benchmark_compare_to_dijkstra():
    print()
    print("Runtime comparison")
    print()

    graphs = get_graphs(3000, current_path / 'graphs.json')

    avg_deg = sum(sum(dict(G.degree()).values()) / G.number_of_nodes() for G in graphs) / len(graphs)
    print("Average degree in test graphs:", avg_deg)

    print("Components: ", [nx.number_connected_components(g) for g in graphs])

    for G in graphs:
        pos = nx.get_node_attributes(G, 'pos')
        for u, v in G.edges():
            dx, dy = pos[u][0] - pos[v][0], pos[u][1] - pos[v][1]
            G[u][v]['weight'] = math.hypot(dx, dy)

    dijkstra = []
    blind_astar = []
    real_astar = []
    for g in graphs:
        try:
            start_time = time.time()
            path1 = nx.dijkstra_path(g, 0, g.number_of_nodes() - 1, weight="weight")
            end_time = time.time()
            dijkstra.append(end_time - start_time)

            start_time = time.time()
            path2 = nx.astar_path(g, 0, g.number_of_nodes() - 1, weight="weight", heuristic=lambda a, b: 0)
            end_time = time.time()
            blind_astar.append(end_time - start_time)

            # noinspection PyShadowingNames
            def dist(u, v):
                dx, dy = g.nodes[u]['pos'][0] - g.nodes[v]['pos'][0], g.nodes[u]['pos'][1] - g.nodes[v]['pos'][1]
                return math.hypot(dx, dy)

            start_time = time.time()
            path3 = nx.astar_path(g, 0, g.number_of_nodes() - 1, weight="weight", heuristic=dist)
            end_time = time.time()
            real_astar.append(end_time - start_time)

            assert path1 == path2 and path1 == path3
        except nx.NetworkXNoPath:
            print("No path found")
            assert False

    print("Dijkstra runtimes:", ["%.3f" % rt for rt in dijkstra])
    print("Average:", sum(dijkstra) / len(dijkstra))

    print("Blind A* runtimes:", ["%.3f" % rt for rt in blind_astar])
    print("Average:", sum(blind_astar) / len(blind_astar))

    print("Real A* runtimes:", ["%.3f" % rt for rt in real_astar])
    print("Average:", sum(real_astar) / len(real_astar))

    assert sum(real_astar) < sum(blind_astar)
    assert sum(blind_astar) < sum(dijkstra)


if __name__ == "__main__":
    benchmark_compare_to_dijkstra()
