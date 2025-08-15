# Generalized Path Finding

This library provides path finding in graphs defined by various input formats and using various algorithms.

The easiest usage is to create a DataProvider of the respective format and create a ready-to-run PathFinder using
the helper provided by the library using reasonable defaults. For example:

```python
from generalized_path_finding import LifDataProvider, create_path_finder

path_finder = create_path_finder(LifDataProvider("tests/formats/lif/LIF_4_4_MAPF.json"))
path = path_finder.find_shortest_path("N_0_2", "N_3_3")

assert path.cost == 4
assert path.nodes == ['N_0_2', 'N_1_2', 'N_2_2', 'N_3_2', 'N_3_3']
assert path.edges == ['E-0_2-1_2', 'E-1_2-2_2', 'E-2_2-3_2', 'E-3_2-3_3']
```

## Library Structure

The library is structured in three layers:

1. **DataProvider**: There are [`DataProvider`](./src/generalized_path_finding/model/data_provider.py)s for different
   file formats of networks. Currently supported are:
    - [Layer Interchange Format][LIF] (by VDMA - Verband Deutscher Maschinen- und Anlagenbau e. V.)
    - Multi Floor Network Excel Schema (used in MediCar 4.0, see examples in [tests/formats/mfn_excel](.
      /tests/formats/mfn_excel))
    - Open Street Map extracts in `.pbf`-files (retreivable from e.g. [Geofabrik](https://download.geofabrik.de/)
      or [Interline](https://www.interline.io/osm/extracts/))
2. **Internal data formats**: `DataProvider`s can provide graph data in different internal formats, the data can be
   converted between internal formats and then used in an algorithm.
3. **Algorithms**: There are several backends implementing the simple
   [`PathFinder`](./src/generalized_path_finding/model/pathfinder.py) interface, each taking at least one of the
   internal data formats. Currently supported are:
    - AStar (implemented by [NetworkX][nx_astar], also usable and performant without heuristic)
    - [RoutingKit](https://github.com/RoutingKit/RoutingKit)
        - taking a pre-processed Contraction Hierarchy
        - taking a NetworkX graph
        - taking a pre-processed graph extract and Contraction Hierarchy from an OpenStreetMap export

[LIF]: https://vdma.org/documents/34570/3317035/FuI_Guideline_LIF_GB.pdf/779bc75c-9525-8d13-412e-fff82bc6ab39?t=1710513623026

[nx_astar]: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.astar.astar_path.html

### A few notes on LIF

- There is a JSON Schema and generated parser available at https://github.com/continua-systems/vdma-lif.
  Our model is handwritten and handles some types and docstrings nicer, while reducing the redundancy of the parsing.
- LIF restricts edges to specific vehicles. That's why, when reading an LIF file into a graph, you have to provide a
  vehicle type if there are multiple present in the file.
- You have the choice of what distance metric to use a weight for the "shortest" path. Available are:
  euclidian distance, manhattan distance, and edge trajectory, as well as the travel time along each of these curves.

## Development Installation

This repository includes the library PyRoutingKit by Laura Doerr and Martin Pouls, who granted their permission to
release this.
RoutingKit itself is included as a git submodule.

To get this repository including the submodule, run:

```shell
git clone https://github.com/fzi-forschungszentrum-informatik/generalized_agv_path_finding.git
cd generalized_agv_path_finding
git submodule update --init --recursive
```

For now, this package uses a virtual environment using Python 3.13 and the packages in requirements.txt.
Frankly, the Pixi configuration in `pyproject.yaml` is dysfunctional at this moment.

```shell
virtualenv .venv
./.venv/Scripts/activate # on Windows
source ./.venv/bin/activate # on Linux/macOS
pip install -r requirements.txt
```

## Testing

The OSM test data is not directly included in this repository.
Before running tests, put `andorra-latest.osm.pbf` into `tests/formats/osm` (you can get it from
https://download.geofabrik.de/europe/andorra-latest.osm.pbf for example).

Do the steps above to create a development environment and in the activated environment, run:

```shell
pytest
```

The first test run will take some minutes, because the graphs for each means of transport has to be extracted from
eh `.osm.pbf` file, but those are cached such that subsequent test runs are much faster.

### Type Checking

This package is dynamically type checked at runtime using [`beartype`](https://github.com/beartype/beartype).
It assumes containers of uniform type for minimal overhead.
The only deviation from its defaults is the enabling of the implicit numeric tower from
[PEP 484](https://peps.python.org/pep-0484/#the-numeric-tower).
