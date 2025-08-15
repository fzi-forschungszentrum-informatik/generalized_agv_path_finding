cmake_minimum_required(VERSION 3.20)
set(CMAKE_CXX_STANDARD 17)
IF(WIN32)
	list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_LIST_DIR}/cpp/dependencies/zlib")
ENDIF()

project(
  ${SKBUILD_PROJECT_NAME}
  VERSION ${SKBUILD_PROJECT_VERSION}
  LANGUAGES CXX)

add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/cpp/dependencies/routingkit")
set_property(TARGET RoutingKit PROPERTY POSITION_INDEPENDENT_CODE ON)

add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/cpp/lib")
set_property(TARGET py-routingkit PROPERTY POSITION_INDEPENDENT_CODE ON)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

python_add_library(_py_routingkit MODULE python/bindings.cpp WITH_SOABI)
target_link_libraries(_py_routingkit PRIVATE pybind11::headers RoutingKit py-routingkit)
target_compile_definitions(_py_routingkit PRIVATE VERSION_INFO=${PROJECT_VERSION})

install(TARGETS _py_routingkit DESTINATION pyroutingkit)