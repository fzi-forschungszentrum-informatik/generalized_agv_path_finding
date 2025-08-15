#pragma once
#include <vector>
#include "pyroutingkit/PointLatLon.h"

namespace fzi::routing {
class RoutingGraph {
public:
    std::vector<unsigned> firstOut;
    std::vector<unsigned> head;
    std::vector<unsigned> tail;
    std::vector<unsigned> travelTime;
    std::vector<unsigned> geoDistance;
    std::vector<std::vector<PointLatLon>> geometry;
    std::vector<uint64_t> osmWayId;
    std::vector<float> latitude;
    std::vector<float> longitude;
    std::vector<uint64_t> osmNodeId;

    unsigned nodeCount() const;

    unsigned arcCount() const;

    void store(const char* filePath) const;

    static RoutingGraph load(const char* filePath);
};

} // namespace fzi::routing