#include "pyroutingkit/RouteArc.h"

namespace fzi::routing {
RouteArc::RouteArc(double duration, double distance, std::vector<PointLatLon>& geometry, uint64_t osmWayId,
                   uint64_t startOsmNodeId, uint64_t endOsmNodeId)
    : duration(duration)
    , distance(distance)
    , geometry(std::move(geometry))
    , osmWayId(osmWayId) 
    , startOsmNodeId(startOsmNodeId) 
    , endOsmNodeId(endOsmNodeId) {
}
} // namespace fzi::routing