add_definitions(-DROUTING_KIT_NO_GCC_EXTENSIONS)

IF (WIN32)
    add_definitions(-DROUTING_KIT_NO_POSIX)
    add_definitions(-DROUTING_KIT_ASSUME_LITTLE_ENDIAN)
ENDIF()

add_library(
RoutingKit
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/bit_select.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/bit_vector.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/buffered_asynchronous_reader.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/compare_vector.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/compute_contraction_hierarchy.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/compute_geographic_distance_weights.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/compute_nested_dissection_order.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/contraction_hierarchy.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/convert_road_dimacs_coordinates.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/convert_road_dimacs_graph.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/customizable_contraction_hierarchy.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/decode_vector.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/encode_vector.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/examine_ch.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/expect.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/export_road_dimacs_graph.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/file_data_source.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/generate_constant_vector.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/generate_dijkstra_rank_test_queries.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/generate_random_node_list.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/generate_random_source_times.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/geo_position_to_node.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/graph_to_dot.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/graph_to_svg.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/graph_util.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/id_mapper.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/nested_dissection.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/osm_decoder.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/osm_extract.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/osm_graph_builder.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/osm_profile.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/osm_simple.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/protobuf.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/randomly_permute_nodes.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/run_contraction_hierarchy_query.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/run_dijkstra.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/show_path.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/strongly_connected_component.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/timer.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/vector_io.cpp"
"${CMAKE_CURRENT_LIST_DIR}/RoutingKit/src/verify.cpp")

IF(WIN32)
	list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_LIST_DIR}/../zlib")
ENDIF()

find_package(ZLIB REQUIRED)

if (ZLIB_FOUND)
    target_include_directories(RoutingKit PUBLIC ${ZLIB_INCLUDE_DIRS})
    target_link_libraries(RoutingKit PRIVATE ${ZLIB_LIBRARIES})
endif (ZLIB_FOUND)

target_include_directories(RoutingKit PUBLIC "${CMAKE_CURRENT_LIST_DIR}/RoutingKit/include")