#include "pyroutingkit/GraphPreparator.h"
#include "pyroutingkit/OsmGraphLoader.h"
#include <routingkit/contraction_hierarchy.h>

namespace fzi::routing {

GraphPreparator::GraphPreparator(const std::string& pbfFilePath)
    : pbfFilePath(pbfFilePath) {
}

void GraphPreparator::prepareCarGraph(const std::string& outputGraphFilePath,
                                      const std::string& outputChFilePath) const {
    prepareGraph(outputGraphFilePath, outputChFilePath, RoutingMode::CAR, 15, 4);
}

void GraphPreparator::prepareBikeGraph(const std::string& outputGraphFilePath, const std::string& outputChFilePath,
                                       unsigned speed) const {
    prepareGraph(outputGraphFilePath, outputChFilePath, RoutingMode::BIKE, speed, 4);
}

void GraphPreparator::preparePedestrianGraph(const std::string& outputGraphFilePath, const std::string& outputChFilePath,
                                             unsigned speed) const {
    prepareGraph(outputGraphFilePath, outputChFilePath, RoutingMode::PEDESTRIAN, 15, speed);
}

void GraphPreparator::prepareGraph(const std::string& outputGraphFilePath, const std::string& outputChFilePath, const RoutingMode routingMode,
                                   unsigned bikeSpeed, unsigned pedestrianSpeed) const {
    OsmGraphLoader loader(pbfFilePath, bikeSpeed, pedestrianSpeed);
    auto graph = loader.loadGraph(routingMode);
    graph.store(outputGraphFilePath.c_str());
    auto ch = RoutingKit::ContractionHierarchy::build(graph.nodeCount(), graph.tail, graph.head, graph.travelTime);
    ch.save_file(outputChFilePath);
}
} // namespace fzi::routing