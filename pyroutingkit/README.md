# Python Package
This project serves as a high-level Python wrapper around [RoutingKit](https://github.com/RoutingKit/RoutingKit).

## Installation

### Installation from PyPi
The package is also published in the internal PyPi repository [ipe-pypi](https://ipe-pypi.fzi.de/). Just install the package with:
```
pip install pyroutingkit
```
This assumes that you have configured the PyPi repository in your `pip.ini` as follows:
```
[global]
extra-index-url = http://ipe:your_password@ipe-pypi.fzi.de
trusted-host = ipe-pypi.fzi.de
```

Pre-built binary wheels may not be available for all platforms and python versions. In this case pip will attempt to build the package from the sources. For this to succeed, you will need a working C++ development environment. Pip version 19.3 is required for usage of the available pre-built binary wheels.

### Installation from sources
To install the `pyroutingkit` Python package from the sources navigate to `src/` and run:
```shell
pip install .
```
For the prerequisites to build the C++ code, see further below.

## Usage
This project allows you to perform routing queries on graphs extracted from OpenStreetMap (OSM) data. To get started, first download an OSM extract in `pbf`-format (for instance from [Geofabrik](https://download.geofabrik.de/) or [Interline](https://www.interline.io/osm/extracts/)). Subsequently, extract the graph and calculate contraction hierarchies. Both the graph and the contraction hierarchies are stored in files.
```python
from pyroutingkit import GraphPreparator

if __name__ == '__main__':
    preparator = GraphPreparator("C:/maps/andorra-latest.osm.pbf")
    preparator.prepareCarGraph("C:/graphs/andorra-latest-car.graph",
                               "C:/graphs/andorra-latest-car.ch")
    preparator.prepareBikeGraph("C:/graphs/andorra-latest-bike.graph",
                                "C:/graphs/andorra-latest-bike.ch",
                                12)
    preparator.preparePedestrianGraph("C:/graphs/andorra-latest-foot.graph",
                                      "C:/graphs/andorra-latest-foot.ch",
                                      3)
```
We support the extraction of graphs for cars, bicycles and pedestrians. In the case of cars, speed limits are gathered based on the OSM data. For bicycles and pedestrians, a fixed speed in kph is supplied in the function call.

You are now ready to perform routing queries:
```python
from pyroutingkit import RoutingService, PointLatLon, Route, DurationAndDistance

if __name__ == '__main__':
    router = RoutingService("C:/temp/andorra-latest-car.graph",
                            "C:/temp/andorra-latest-car.ch",
                            1000)
    origin = PointLatLon(42.46333811337092, 1.489878394942694)
    destination = PointLatLon(42.50946473317848, 1.5397046939511791)

    duration = router.duration(origin, destination)
    duration_and_distance: DurationAndDistance = router.durationAndDistance(origin, destination)
    route: Route = router.route(origin, destination)
```
Upon performing a routing query, the origin and destination are first matched to nodes in the routing network. The third argument passed to the `RoutingService` defines the radius in meters up to which points are matched to the road network. Points outside this radius of the nearest routing node cannot be used for routing.

Subsequently, the fastest route from the origin to the destination can be determined. We provide three functions for routing queries. `RoutingService.duration` only calculates the duration and is significantly faster than the other two options. `RoutingService.durationAndDistance` returns the duration and distance of the route, while `RoutingService.route` also returns the complete geometry of the route.

## Publishing the package

### Windows
Windows version cannot be built in the CI-Pipeline and must therefore be published manually. To publish a new version of the package to the internal PyPi repository, follow these steps:
- Increment the package version in `pyproject.toml`.
- Build the package with `python -m build`.
- Upload the package with `twine upload -r ipe-pypi dist/*`.

This assumes that you have configured the repository `ipe-pypi` in your `.pypirc` as follows:
```
...
[distutils]
index-servers =
    ipe-pypi
    
[ipe-pypi]
repository = https://ipe-pypi.fzi.de
username = ipe
password = your_password
...
```

### Linux
Linux versions are built in CI-Pipeline, see `gitlab-ci.yml` for details.

# Development
This project uses [CMake](https://cmake.org/) to build. For the python bindings we utilize [pybind11](https://github.com/pybind/pybind11) and [scikit-build](https://github.com/scikit-build/scikit-build).

## Dependencies
We rely on [RoutingKit](https://github.com/RoutingKit/RoutingKit) and [zlib](https://github.com/madler/zlib) as external dependencies. `RoutingKit` is included as submodule in this repo and built from the sources, so use `git clone --recurse-submodules` or `git submodule update --init` when cloning the project. 

`zlib` binaries for Windows are included in the project. Alternatively, install `zlib` via [vcpkg](https://vcpkg.io/en/):

```
vcpkg install zlib:x64-windows
```

Under Linux install `zlib`:
```
sudo apt-get install zlib1g-dev
```
