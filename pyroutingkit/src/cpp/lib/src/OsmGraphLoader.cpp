#include "pyroutingkit/OsmGraphLoader.h"
#include <pyroutingkit/LargestComponentFilter.h>
#include <routingkit/osm_profile.h>
#include <stdexcept>

namespace fzi::routing {

OsmGraphLoader::OsmGraphLoader(const std::string& pbfFilePath, unsigned bikeSpeed, unsigned pedestrianSpeed)
    : pbfFilePath(pbfFilePath)
    , bikeSpeed(bikeSpeed)
    , pedestrianSpeed(pedestrianSpeed) {
}

RoutingGraph OsmGraphLoader::loadGraph(const RoutingMode routingMode) {
    auto osmMapping = loadOsmMapping(routingMode);
    unsigned routingWayCount = osmMapping.is_routing_way.population_count();
    RoutingKit::IDMapper nodeMapping(osmMapping.is_routing_node);
    RoutingKit::IDMapper wayMapping(osmMapping.is_routing_way);
    std::vector<unsigned> waySpeed(routingWayCount);
    auto osmGraph = loadOsmRoutingGraph(osmMapping, waySpeed, routingMode);
    auto graph = initializeRoutingGraphFromOsmGraph(osmGraph);
    determineArcAttributes(graph, osmGraph, waySpeed, wayMapping);
    determineNodeAttributes(graph, nodeMapping);
    LargestComponentFilter sccFilter(graph);
    return sccFilter.filterLargestComponent();
}

void OsmGraphLoader::determineArcAttributes(RoutingGraph& graph, const RoutingKit::OSMRoutingGraph& osmGraph,
                                            const std::vector<unsigned>& waySpeed,
                                            const RoutingKit::IDMapper& wayMapping) {
    for (unsigned arcIndex = 0; arcIndex < graph.arcCount(); ++arcIndex) {
        graph.travelTime[arcIndex] *= 18000;
        graph.travelTime[arcIndex] /= waySpeed[osmGraph.way[arcIndex]];
        graph.travelTime[arcIndex] /= 5;
        graph.osmWayId.push_back(wayMapping.to_global(osmGraph.way[arcIndex]));
        std::vector<PointLatLon> arcGeometry;
        arcGeometry.push_back(PointLatLon(graph.latitude[graph.tail[arcIndex]], graph.longitude[graph.tail[arcIndex]]));
        for (auto modellingNodeIndex = osmGraph.first_modelling_node[arcIndex];
             modellingNodeIndex < osmGraph.first_modelling_node[arcIndex + 1]; ++modellingNodeIndex) {
            arcGeometry.push_back(PointLatLon(osmGraph.modelling_node_latitude[modellingNodeIndex],
                                              osmGraph.modelling_node_longitude[modellingNodeIndex]));
        }
        arcGeometry.push_back(PointLatLon(graph.latitude[graph.head[arcIndex]], graph.longitude[graph.head[arcIndex]]));
        graph.geometry.push_back(arcGeometry);
    }
}

void OsmGraphLoader::determineNodeAttributes(RoutingGraph& graph, const RoutingKit::IDMapper& nodeMapping) {
    for (unsigned nodeIndex = 0; nodeIndex < graph.nodeCount(); ++nodeIndex) {
        graph.osmNodeId.push_back(nodeMapping.to_global(nodeIndex));
    }
}

RoutingGraph OsmGraphLoader::initializeRoutingGraphFromOsmGraph(const RoutingKit::OSMRoutingGraph& osmGraph) {
    RoutingGraph graph;
    graph.firstOut = osmGraph.first_out;
    graph.head = osmGraph.head;
    graph.tail = RoutingKit::invert_inverse_vector(graph.firstOut);
    graph.latitude = osmGraph.latitude;
    graph.longitude = osmGraph.longitude;
    graph.geoDistance = osmGraph.geo_distance;
    graph.travelTime = graph.geoDistance;
    graph.geometry.reserve(graph.arcCount());
    graph.osmWayId.reserve(graph.arcCount());
    graph.osmNodeId.reserve(graph.nodeCount());
    return graph;
}

RoutingKit::OSMRoutingGraph OsmGraphLoader::loadOsmRoutingGraph(const RoutingKit::OSMRoutingIDMapping& osmMapping,
                                                                std::vector<unsigned>& waySpeed,
                                                                const RoutingMode routingMode) {
    std::function<RoutingKit::OSMWayDirectionCategory(uint64_t, unsigned, const RoutingKit::TagMap&)> wayCallback =
        [&](uint64_t osmWayId, unsigned routingWayId, const RoutingKit::TagMap& wayTags) {
            if (routingMode == RoutingMode::CAR) {
                waySpeed[routingWayId] = get_osm_way_speed(osmWayId, wayTags, nullptr);
                return get_osm_car_direction_category(osmWayId, wayTags, nullptr);
            } else if (routingMode == RoutingMode::BIKE) {
                waySpeed[routingWayId] = bikeSpeed;
                return get_osm_bicycle_direction_category(osmWayId, wayTags, nullptr);
            } else if (routingMode == RoutingMode::PEDESTRIAN) {
                waySpeed[routingWayId] = pedestrianSpeed;
                return RoutingKit::OSMWayDirectionCategory::open_in_both;
            }
            throw std::runtime_error("Invalid routing mode!");
        };

    return RoutingKit::load_osm_routing_graph_from_pbf(
        pbfFilePath, osmMapping, wayCallback,
        [&](uint64_t osmRelationId, const std::vector<RoutingKit::OSMRelationMember>& memberList,
            const RoutingKit::TagMap& tags, std::function<void(RoutingKit::OSMTurnRestriction)> onNewRestriction) {
            return decode_osm_car_turn_restrictions(osmRelationId, memberList, tags, onNewRestriction, nullptr);
        },
        nullptr, false, RoutingKit::OSMRoadGeometry::uncompressed);
}

bool strEq(const char*l, const char*r){
	return !strcmp(l, r);
}

bool isParkingAisle(const RoutingKit::TagMap& tags) {
    const char* service = tags["service"];
    if (service != nullptr && strEq(service, "parking_aisle")) {
        return true;
    }
    return false;
}

RoutingKit::OSMRoutingIDMapping OsmGraphLoader::loadOsmMapping(const RoutingMode routingMode) const {
    std::function<bool(uint64_t, const RoutingKit::TagMap&)> isWayUsed = [&](uint64_t osmWayId,
                                                                             const RoutingKit::TagMap& tags) {
        if (routingMode == RoutingMode::CAR) {
            return is_osm_way_used_by_cars(osmWayId, tags, nullptr) && !isParkingAisle(tags);
        } else if (routingMode == RoutingMode::BIKE) {
            return is_osm_way_used_by_bicycles(osmWayId, tags, nullptr) && !isParkingAisle(tags);
        } else if (routingMode == RoutingMode::PEDESTRIAN) {
            return is_osm_way_used_by_pedestrians(osmWayId, tags, nullptr) && !isParkingAisle(tags);
        }
        throw std::runtime_error("Invalid routing mode!");
    };

    return RoutingKit::load_osm_id_mapping_from_pbf(pbfFilePath, nullptr, isWayUsed, nullptr, false);
}

} // namespace fzi::routing