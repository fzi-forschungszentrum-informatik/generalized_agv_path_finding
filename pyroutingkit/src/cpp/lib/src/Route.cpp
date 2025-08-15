#include "pyroutingkit/Route.h"
#include <sstream>
#include <iomanip>

namespace fzi::routing {

Route::Route(double duration, double distance, std::vector<RouteArc>& arcs)
    : duration(duration)
    , distance(distance)
    , arcs(std::move(arcs)) {
}

std::string Route::toWkt() const {
    std::stringstream stream;
    stream << "LINESTRING(";
    stream << std::fixed << std::setprecision(6);
    for (auto arcIndex = 0; arcIndex < arcs.size(); ++arcIndex) {
        const auto& arc = arcs[arcIndex];
        auto geometryOffset = arcIndex == arcs.size() - 1 ? 0 : 1;
        for (auto pointIndex = 0; pointIndex < arc.geometry.size() - geometryOffset; ++pointIndex) {
            const auto& point = arc.geometry[pointIndex];
            stream << point.longitude << " " << point.latitude;
            if (arcIndex != arcs.size() - 1 || pointIndex != arc.geometry.size() - 1) {
                stream << ", ";
            }
        }
    }
    stream << ")";
    return stream.str();
}
} // namespace fzi::routing