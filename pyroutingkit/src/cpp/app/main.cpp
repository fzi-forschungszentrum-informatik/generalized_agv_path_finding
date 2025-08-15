#include <algorithm>
#include <chrono>
#include <execution>
#include <iostream>
#include <numeric>
#include <pyroutingkit/GraphPreparator.h>
#include <pyroutingkit/OsmGraphLoader.h>
#include <pyroutingkit/RoutingGraph.h>
#include <pyroutingkit/RoutingService.h>
#include <routingkit/contraction_hierarchy.h>

using namespace fzi::routing;

int main(int argc, char* argv[]) {
    //GraphPreparator preparator("C:/temp/germany-latest.osm.pbf");
    //preparator.prepareCarGraph("C:/temp/germany-latest-car.graph", "C:/temp/germany-latest-car.ch");

    // RoutingService service("C:/temp/karlsruhe-bike.graph", "C:/temp/karlsruhe-bike.ch");
    // auto origin = PointLatLon(49.02076098503358, 8.445475014267148);
    // auto destination = PointLatLon(49.020286807240204, 8.448186789607776);
    // auto route = service.route(origin, destination);
    // std::cout << route.duration << std::endl;
    // std::cout << route.distance << std::endl;
    // std::cout << route.toWkt() << std::endl;

    RoutingService service("C:/temp/germany-latest-car.graph", "C:/temp/germany-latest-car.ch", 1000);
    auto origin = PointLatLon(49.01173507183336, 8.424533607221871);
    auto destination = PointLatLon(52.51060956643967, 13.38994576319864);

    auto numCalls = 10000;

    auto start = std::chrono::high_resolution_clock::now();
    auto route = service.route(origin, destination);
    for (auto i = 0; i < numCalls - 1; ++i) {
        route = service.route(origin, destination);
    }
    auto end = std::chrono::high_resolution_clock::now();
    auto avgCallDuration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count() /
    static_cast<double>(numCalls); std::cout << "Avg. running time (route): " << avgCallDuration << std::endl;

    start = std::chrono::high_resolution_clock::now();
    auto durationAndDistance = service.durationAndDistance(origin, destination);
    for (auto i = 0; i < numCalls - 1; ++i) {
        durationAndDistance = service.durationAndDistance(origin, destination);
    }
    end = std::chrono::high_resolution_clock::now();
    avgCallDuration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count() /
    static_cast<double>(numCalls); std::cout << "Avg. running time (duration+distance): " << avgCallDuration <<
    std::endl;

    start = std::chrono::high_resolution_clock::now();
    auto duration = service.duration(origin, destination);
    for (auto i = 0; i < numCalls - 1; ++i) {
        duration = service.duration(origin, destination);
    }
    end = std::chrono::high_resolution_clock::now();
    avgCallDuration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count() /
    static_cast<double>(numCalls); std::cout << "Avg. running time (duration): " << avgCallDuration << std::endl;

    std::cout << route.toWkt() << std::endl;
}