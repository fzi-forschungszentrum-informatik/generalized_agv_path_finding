add_library(py-routingkit
"src/OsmGraphLoader.cpp"
"src/GraphPreparator.cpp" 
"src/RoutingService.cpp" 
"src/PointLatLon.cpp" 
"src/Route.cpp" 
"src/RouteArc.cpp"
"src/RoutingGraph.cpp"
"src/DurationAndDistance.cpp" 
"src/LargestComponentFilter.cpp")

target_include_directories(py-routingkit PUBLIC "./include")
target_link_libraries(py-routingkit PRIVATE RoutingKit)