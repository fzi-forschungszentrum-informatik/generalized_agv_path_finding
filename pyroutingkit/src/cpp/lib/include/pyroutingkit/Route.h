#pragma once
#include "pyroutingkit/RouteArc.h"
#include <vector>

namespace fzi::routing {
class Route {
public:
    Route(double duration, double distance, std::vector<RouteArc>& arcs);

    double duration;
    double distance;
    std::vector<RouteArc> arcs;

    std::string toWkt() const;
};
} // namespace fzi::routing