#pragma once

namespace fzi::routing {
class DurationAndDistance {
public:
    DurationAndDistance(double duration, double distance);

    double duration;
    double distance;
};
} // namespace fzi::routing