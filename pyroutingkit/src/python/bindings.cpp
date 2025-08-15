#include <iostream>
#include <memory>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pyroutingkit/GraphPreparator.h>
#include <pyroutingkit/PointLatLon.h>
#include <pyroutingkit/Route.h>
#include <pyroutingkit/RouteArc.h>
#include <pyroutingkit/RoutingService.h>
#include <routingkit/contraction_hierarchy.h>

namespace py = pybind11;

/**
 * Build a ContractionHierarchy from a list of edges and save it to a file.
 */
static void buildContractionHierarchy(
    size_t node_count,
    const std::vector<std::tuple<unsigned, unsigned, unsigned>>& edges,
    const std::string& ch_output_file
){
    // Prepare vectors of tail, head, and weight
    std::vector<unsigned> tail, head, weight;
    tail.reserve(edges.size());
    head.reserve(edges.size());
    weight.reserve(edges.size());

    // Unpack tuples (tail, head, weight)
    for(const auto& e : edges){
        tail.push_back(std::get<0>(e));
        head.push_back(std::get<1>(e));
        weight.push_back(std::get<2>(e));
    }

    // Build the ContractionHierarchy
    auto ch = RoutingKit::ContractionHierarchy::build(node_count, tail, head, weight);

    // Save it to a file
    ch.save_file(ch_output_file);
}

/**
 * Load a ContractionHierarchy from a file and return a shared_ptr to it.
 * The returned object can be reused for multiple queries.
 */
static std::shared_ptr<RoutingKit::ContractionHierarchy> loadContractionHierarchy(
    const std::string& ch_file
){
    // Load ContractionHierarchy from file and return a shared_ptr to it
    // The CH object will be automatically managed by the shared_ptr
    return std::make_shared<RoutingKit::ContractionHierarchy>(RoutingKit::ContractionHierarchy::load_file(ch_file));
}

/**
 * Query the shortest path using a loaded ContractionHierarchy, given source and target node IDs.
 * Returns a vector of arc indices describing the path.
 */
static py::tuple queryContractionHierarchyPath(
    const std::shared_ptr<RoutingKit::ContractionHierarchy>& ch,
    unsigned source,
    unsigned target
) {
    // Create and run the query
    RoutingKit::ContractionHierarchyQuery ch_query(*ch);
    ch_query.reset().add_source(source).add_target(target).run();

    std::vector<unsigned> arc_indices = ch_query.get_arc_path();
    unsigned total_distance = ch_query.get_distance();

    // Return (arc_indices, total_distance) as a Python tuple
    // this copies node_indices from C++ to Python (which is fine)
    return py::make_tuple(arc_indices, total_distance);
}


PYBIND11_MODULE(_py_routingkit, m) {
    m.doc() = R"pbdoc(
        Python Wrapped C++ Routing
        -----------------------

        .. currentmodule:: py_routingkit

        .. autosummary::
           :toctree: _generate

           PointLatLon
           RoutingService
            duration
            durationAndDistance
            route
           GraphPreparator
            prepareGraph
           ContractionHierarchy
            load_contraction_hierarchy
            query_contraction_hierarchy_path
    )pbdoc";

    py::class_<RoutingKit::ContractionHierarchy, std::shared_ptr<RoutingKit::ContractionHierarchy>>(m, "ContractionHierarchy");

    py::class_<fzi::routing::DurationAndDistance>(m, "DurationAndDistance")
        .def(py::init<double, double>())
        .def_readwrite("duration", &fzi::routing::DurationAndDistance::duration)
        .def_readwrite("distance", &fzi::routing::DurationAndDistance::distance);

    py::class_<fzi::routing::PointLatLon>(m, "PointLatLon")
        .def(py::init<double, double>())
        .def_readwrite("latitude", &fzi::routing::PointLatLon::latitude)
        .def_readwrite("longitude", &fzi::routing::PointLatLon::longitude);

    py::class_<fzi::routing::RouteArc>(m, "RouteArc")
        .def_readwrite("duration", &fzi::routing::RouteArc::duration)
        .def_readwrite("distance", &fzi::routing::RouteArc::distance)
        .def_readwrite("geometry", &fzi::routing::RouteArc::geometry)
        .def_readwrite("startOsmNodeId", &fzi::routing::RouteArc::startOsmNodeId)
        .def_readwrite("endOsmNodeId", &fzi::routing::RouteArc::endOsmNodeId)
        .def_readwrite("osmWayId", &fzi::routing::RouteArc::osmWayId)
        .def(py::init<double, double, std::vector<fzi::routing::PointLatLon>&, uint64_t, uint64_t, uint64_t>());

    py::class_<fzi::routing::Route>(m, "Route")
        .def(py::init<double, double, std::vector<fzi::routing::RouteArc>&>())
        .def_readwrite("duration", &fzi::routing::Route::duration)
        .def_readwrite("distance", &fzi::routing::Route::distance)
        .def_readwrite("arcs", &fzi::routing::Route::arcs)
        .def("toWkt", &fzi::routing::Route::toWkt);

    py::class_<fzi::routing::RoutingService>(m, "RoutingService")
        .def(py::init<const std::string&, const std::string&, unsigned>(),
            py::arg("graphFilePath"), py::arg("chFilePath"), py::arg("matchingRadius"))
        .def("duration", &fzi::routing::RoutingService::duration)
        .def("durationAndDistance", &fzi::routing::RoutingService::durationAndDistance)
        .def("route", &fzi::routing::RoutingService::route);

    py::enum_<RoutingMode>(m, "RoutingMode")
        .value("CAR", RoutingMode::CAR)
        .value("BIKE", RoutingMode::BIKE)
        .value("PEDESTRIAN", RoutingMode::PEDESTRIAN)
        .export_values();

    py::class_<fzi::routing::GraphPreparator>(m, "GraphPreparator")
        .def(py::init<const std::string&>())
        .def("prepareCarGraph", &fzi::routing::GraphPreparator::prepareCarGraph)
        .def("prepareBikeGraph", &fzi::routing::GraphPreparator::prepareBikeGraph)
        .def("preparePedestrianGraph", &fzi::routing::GraphPreparator::preparePedestrianGraph)
        .def("prepareGraph",
            &fzi::routing::GraphPreparator::prepareGraph,
            py::arg("outputGraphFilePath"),
            py::arg("outputChFilePath"),
            py::arg("routingMode") = RoutingMode::CAR,
            py::arg("bikeSpeed") = 15,
            py::arg("pedestrianSpeed") = 4
        );

    m.def(
        "build_contraction_hierarchy",
        &buildContractionHierarchy,
        py::arg("node_count"),
        py::arg("edges"),
        py::arg("ch_output_file"),
        R"pbdoc(
            Build a ContractionHierarchy from a list of (tail, head, weight) edges
            and save it to a specified file.

            :param node_count: Number of nodes in the graph.
            :param edges: A list of (tail, head, weight) tuples describing each arc.
            :param ch_output_file: Path where the resulting .ch file is saved.
        )pbdoc"
    );

    m.def(
        "load_contraction_hierarchy",
        &loadContractionHierarchy,
        py::arg("ch_file"),
        R"pbdoc(
            Load a ContractionHierarchy from a file and return it for use in multiple queries.

            :param ch_file: Path to the ContractionHierarchy file.
            :return: A shared_ptr to the loaded ContractionHierarchy object that can be reused for multiple queries.

            Note: Memory management is handled automatically through the shared_ptr.
        )pbdoc"
    );

    m.def(
        "query_contraction_hierarchy_path",
        py::overload_cast<const std::shared_ptr<RoutingKit::ContractionHierarchy>&, unsigned, unsigned>(&queryContractionHierarchyPath),
        py::arg("ch"),
        py::arg("source"),
        py::arg("target"),
        R"pbdoc(
            Run a shortest-path query on a loaded ContractionHierarchy.
            Returns a 2-tuple containing:
            (2) A list of arcs as indices into the original edge list
            (3) The total weight (distance) of the path

            :param ch: A shared_ptr to a loaded ContractionHierarchy object.
            :param source: Source node index.
            :param target: Target node index.
        )pbdoc"
    );

}