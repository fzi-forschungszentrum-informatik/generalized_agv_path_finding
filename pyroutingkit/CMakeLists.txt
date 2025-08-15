cmake_minimum_required(VERSION 3.20)
set(CMAKE_CXX_STANDARD 17)

project("py-routingkit")

add_subdirectory("src/cpp/dependencies/routingkit")
add_subdirectory("src/cpp/lib")
add_subdirectory("src/cpp/test")
add_subdirectory("src/cpp/app")