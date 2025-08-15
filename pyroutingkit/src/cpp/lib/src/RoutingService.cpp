#include "pyroutingkit/RoutingService.h"
#include <routingkit/constants.h>
#include <stdexcept>

namespace fzi::routing {
thread_local RoutingKit::ContractionHierarchyQuery RoutingService::chQuery = RoutingKit::ContractionHierarchyQuery();

RoutingService::RoutingService(const std::string& graphFilePath, const std::string& chFilePath, unsigned matchingRadius)
    : graph(RoutingGraph::load(graphFilePath.c_str()))
    , nodeIndex(graph.latitude, graph.longitude)
    , ch(RoutingKit::ContractionHierarchy::load_file(chFilePath))
    , matchingRadius(matchingRadius) {
}

double RoutingService::duration(const PointLatLon& origin, const PointLatLon& destination) const {
    runChQuery(origin, destination);
    if (chQuery.shortest_path_meeting_node == RoutingKit::invalid_id) {
        throw std::runtime_error("Could not find path from " + origin.toString() + " to " + destination.toString());
    }
    return static_cast<double>(chQuery.get_distance()) / 1000.0;
}

DurationAndDistance RoutingService::durationAndDistance(const PointLatLon& origin, const PointLatLon& destination) const {
    runChQuery(origin, destination);
    auto duration = static_cast<double>(chQuery.get_distance()) / 1000.0;
    auto distance = 0.0;
    auto arcs = chQuery.get_arc_path();
    for (const auto& arc : arcs) {
        distance += graph.geoDistance[arc];
    }
    return DurationAndDistance(duration, distance);
}

Route RoutingService::route(const PointLatLon& origin, const PointLatLon& destination) const {
    runChQuery(origin, destination);
    auto duration = static_cast<double>(chQuery.get_distance()) / 1000.0;
    auto distance = 0.0;
    std::vector<RouteArc> routeArcs;
    auto arcs = chQuery.get_arc_path();
    routeArcs.reserve(arcs.size());
    for (auto arcIndex = 0; arcIndex < arcs.size(); ++arcIndex) {
        const auto& arc = arcs[arcIndex];
        distance += graph.geoDistance[arc];
        std::vector<PointLatLon> geometry = std::vector<PointLatLon>(graph.geometry[arc].begin(), graph.geometry[arc].end());
        RouteArc routeArc(graph.travelTime[arc] / 1000.0, graph.geoDistance[arc], geometry, graph.osmWayId[arc],
                          graph.osmNodeId[graph.tail[arc]], graph.osmNodeId[graph.head[arc]]);
        routeArcs.push_back(std::move(routeArc));
    }
    Route route(duration, distance, routeArcs);
    return route;
}

void RoutingService::initializeChQuery() const {
    if (!(chQuery.ch == &ch)) {
        chQuery.reset(ch);
    }
}

void RoutingService::runChQuery(const PointLatLon& origin, const PointLatLon& destination) const {
    const auto originNode = matchPointToGraph(origin);
    const auto destinationNode = matchPointToGraph(destination);
    initializeChQuery();
    chQuery.reset().add_source(originNode).add_target(destinationNode).run();
}

unsigned RoutingService::matchPointToGraph(const PointLatLon& point) const {
    auto node = nodeIndex.find_nearest_neighbor_within_radius(point.latitude, point.longitude, matchingRadius).id;
    if (node != RoutingKit::invalid_id) {
        return node;
    }
    throw std::runtime_error("Could not match point " + point.toString() + " to graph!");
}
} // namespace fzi::routing