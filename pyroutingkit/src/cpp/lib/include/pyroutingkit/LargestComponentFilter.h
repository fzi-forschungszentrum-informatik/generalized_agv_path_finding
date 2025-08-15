#pragma once
#include <pyroutingkit/RoutingGraph.h>

namespace fzi::routing {
class LargestComponentFilter {
public:
    LargestComponentFilter(RoutingGraph& graph);

    RoutingGraph filterLargestComponent() const;

private:
    RoutingGraph& graph;

    void processNode(size_t nodeIndex, RoutingGraph& connectedGraph, const std::vector<bool>& largestScc,
                     const std::vector<unsigned>& newNodeIndices) const;
    void processArc(size_t arcIndex, RoutingGraph& connectedGraph, const std::vector<bool>& largestScc,
                    const std::vector<unsigned>& newNodeIndices) const;
    void applyPermutations(RoutingGraph& connectedGraph) const;
    std::vector<unsigned> determineNewNodeIndices(const std::vector<bool>& largestScc) const;
    RoutingGraph initializeConnectedGraph() const;
};
} // namespace fzi::routing