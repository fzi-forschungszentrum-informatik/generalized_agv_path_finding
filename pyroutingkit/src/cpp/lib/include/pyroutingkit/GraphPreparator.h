#pragma once
#include <string>
#include <pyroutingkit/RoutingMode.h>

namespace fzi::routing {
class GraphPreparator {
public:
    GraphPreparator(const std::string& pbfFilePath);
    void prepareCarGraph(const std::string& outputGraphFilePath, const std::string& outputChFilePath) const;
    void prepareBikeGraph(const std::string& outputGraphFilePath, const std::string& outputChFilePath, unsigned speed) const;
    void preparePedestrianGraph(const std::string& outputGraphFilePath, const std::string& outputChFilePath,
                                unsigned speed) const;
    void prepareGraph(const std::string& outputGraphFilePath, const std::string& outputChFilePath,
                      const RoutingMode routingMode, unsigned bikeSpeed, unsigned pedestrianSpeed) const;

private:
    std::string pbfFilePath;
};

} // namespace fzi::routing