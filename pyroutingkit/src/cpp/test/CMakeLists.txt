enable_testing()

add_executable(py-routingkit-test 
"GraphPreparatorTest.cpp" )

find_package(GTest REQUIRED)
target_link_libraries(py-routingkit-test PRIVATE GTest::gtest GTest::gtest_main py-routingkit RoutingKit)
