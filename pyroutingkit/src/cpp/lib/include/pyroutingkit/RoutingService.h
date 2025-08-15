#pragma once
#include <string>
#include <routingkit/geo_position_to_node.h>
#include "pyroutingkit/Route.h"
#include <routingkit/contraction_hierarchy.h>
#include "pyroutingkit/RoutingGraph.h"
#include "pyroutingkit/DurationAndDistance.h"

namespace fzi::routing {
    class RoutingService {
    public:
        RoutingService(const std::string& graphFilePath, const std::string& chFilePath, unsigned matchingRadius);
        double duration(const PointLatLon& origin, const PointLatLon& destination) const;
        DurationAndDistance durationAndDistance(const PointLatLon& origin, const PointLatLon& destination) const;
        Route route(const PointLatLon& origin, const PointLatLon& destination) const;

    private:
        RoutingGraph graph;
        RoutingKit::GeoPositionToNode nodeIndex;
        RoutingKit::ContractionHierarchy ch;
        unsigned matchingRadius;
        static thread_local RoutingKit::ContractionHierarchyQuery chQuery;

        void initializeChQuery() const;
        void runChQuery(const PointLatLon& origin, const PointLatLon& destination) const;
        unsigned matchPointToGraph(const PointLatLon& point) const;
    };
}