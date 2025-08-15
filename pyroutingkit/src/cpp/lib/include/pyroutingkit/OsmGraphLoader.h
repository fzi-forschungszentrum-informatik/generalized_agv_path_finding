#pragma once
#include "pyroutingkit/RoutingGraph.h"
#include "pyroutingkit/RoutingMode.h"
#include <routingkit/id_mapper.h>
#include <routingkit/osm_graph_builder.h>
#include <routingkit/osm_simple.h>
#include <string>

namespace fzi::routing {
class OsmGraphLoader {
public:
    OsmGraphLoader(const std::string& pbfFilePath, unsigned bikeSpeed, unsigned pedestrianSpeed);
    RoutingGraph loadGraph(const RoutingMode routingMode);

private:
    std::string pbfFilePath;
    unsigned bikeSpeed;
    unsigned pedestrianSpeed;

    void determineArcAttributes(RoutingGraph& graph, const RoutingKit::OSMRoutingGraph& osmGraph,
                                const std::vector<unsigned>& waySpeed, const RoutingKit::IDMapper& wayMapping);
    void determineNodeAttributes(RoutingGraph& graph, const RoutingKit::IDMapper& nodeMapping);
    RoutingGraph initializeRoutingGraphFromOsmGraph(const RoutingKit::OSMRoutingGraph& osmGraph);
    RoutingKit::OSMRoutingIDMapping loadOsmMapping(const RoutingMode routingMode) const;
    RoutingKit::OSMRoutingGraph loadOsmRoutingGraph(const RoutingKit::OSMRoutingIDMapping& osmMapping,
                                                    std::vector<unsigned>& way_speed, const RoutingMode routingMode);
};
} // namespace fzi::routing