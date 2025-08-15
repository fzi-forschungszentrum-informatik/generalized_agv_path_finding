#include <pyroutingkit/LargestComponentFilter.h>
#include <routingkit/constants.h>
#include <routingkit/strongly_connected_component.h>
#include <routingkit/sort.h>
#include <routingkit/inverse_vector.h>

namespace fzi::routing {

LargestComponentFilter::LargestComponentFilter(RoutingGraph& graph)
    : graph(graph) {
}

RoutingGraph LargestComponentFilter::filterLargestComponent() const {
    auto largestScc = RoutingKit::compute_largest_strongly_connected_component(graph.firstOut, graph.head);
    auto newNodeIndices = determineNewNodeIndices(largestScc);
    RoutingGraph connectedGraph = initializeConnectedGraph();
    
    for (auto nodeIndex = 0; nodeIndex < graph.nodeCount(); ++nodeIndex) {
        if (largestScc[nodeIndex]) {
            processNode(nodeIndex, connectedGraph, largestScc, newNodeIndices);
        }
    }

    applyPermutations(connectedGraph);
    return connectedGraph;
}

void LargestComponentFilter::processNode(size_t nodeIndex, RoutingGraph& connectedGraph,
                                         const std::vector<bool>& largestScc,
                                         const std::vector<unsigned>& newNodeIndices) const {
    connectedGraph.latitude.push_back(graph.latitude[nodeIndex]);
    connectedGraph.longitude.push_back(graph.longitude[nodeIndex]);
    connectedGraph.osmNodeId.push_back(graph.osmNodeId[nodeIndex]);
    for (auto arcIndex = graph.firstOut[nodeIndex]; arcIndex < graph.firstOut[nodeIndex + 1]; ++arcIndex) {
        processArc(arcIndex, connectedGraph, largestScc, newNodeIndices);
    }
}

void LargestComponentFilter::processArc(size_t arcIndex, RoutingGraph& connectedGraph,
                                        const std::vector<bool>& largestScc,
                                        const std::vector<unsigned>& newNodeIndices) const {
    auto head = graph.head[arcIndex];
    if (largestScc[head])
    {
        auto tail = graph.tail[arcIndex];
        connectedGraph.head.push_back(newNodeIndices[head]);
        connectedGraph.tail.push_back(newNodeIndices[tail]);
        connectedGraph.travelTime.push_back(graph.travelTime[arcIndex]);
        connectedGraph.geoDistance.push_back(graph.geoDistance[arcIndex]);
        connectedGraph.geometry.push_back(std::move(graph.geometry[arcIndex]));
        connectedGraph.osmWayId.push_back(graph.osmWayId[arcIndex]);
    }
}

void LargestComponentFilter::applyPermutations(RoutingGraph& connectedGraph) const {
    auto permutation = RoutingKit::compute_sort_permutation_using_less(connectedGraph.tail);
    connectedGraph.tail = RoutingKit::apply_permutation(permutation, connectedGraph.tail);
    connectedGraph.head = RoutingKit::apply_permutation(permutation, connectedGraph.head);
    connectedGraph.travelTime = RoutingKit::apply_permutation(permutation, connectedGraph.travelTime);
    connectedGraph.geoDistance = RoutingKit::apply_permutation(permutation, connectedGraph.geoDistance);
    connectedGraph.geometry = RoutingKit::apply_permutation(permutation, connectedGraph.geometry);
    connectedGraph.osmWayId = RoutingKit::apply_permutation(permutation, connectedGraph.osmWayId);
    connectedGraph.firstOut = RoutingKit::invert_vector(connectedGraph.tail, connectedGraph.latitude.size());
}

std::vector<unsigned> LargestComponentFilter::determineNewNodeIndices(const std::vector<bool>& largestScc) const {
    std::vector<unsigned> newNodeIndices(graph.nodeCount(), RoutingKit::invalid_id);
    unsigned newNodIndex = 0;
    for (auto nodeIndex = 0; nodeIndex < graph.nodeCount(); ++nodeIndex) {
        if (largestScc[nodeIndex]) {
            newNodeIndices[nodeIndex] = newNodIndex++;
        }
    }
    return newNodeIndices;
}

RoutingGraph LargestComponentFilter::initializeConnectedGraph() const {
    RoutingGraph connectedGraph;
    connectedGraph.head.reserve(graph.arcCount());
    connectedGraph.tail.reserve(graph.arcCount());
    connectedGraph.geoDistance.reserve(graph.arcCount());
    connectedGraph.travelTime.reserve(graph.arcCount());
    connectedGraph.geometry.reserve(graph.arcCount());
    connectedGraph.osmWayId.reserve(graph.arcCount());
    connectedGraph.latitude.reserve(graph.nodeCount());
    connectedGraph.longitude.reserve(graph.nodeCount());
    connectedGraph.osmNodeId.reserve(graph.nodeCount());
    return connectedGraph;
}

} // namespace fzi::routing