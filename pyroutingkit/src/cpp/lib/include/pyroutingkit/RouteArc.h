#pragma once
#include "pyroutingkit/PointLatLon.h"
#include <vector>

namespace fzi::routing {
class RouteArc {
public:
    RouteArc(double duration, double distance, std::vector<PointLatLon>& geometry, uint64_t osmWayId,
             uint64_t startOsmNodeId, uint64_t endOsmNodeId);

    double duration;
    double distance;
    std::vector<PointLatLon> geometry;
    uint64_t osmWayId;
    uint64_t startOsmNodeId;
    uint64_t endOsmNodeId;
};
} // namespace fzi::routing