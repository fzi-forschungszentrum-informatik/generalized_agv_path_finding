add_executable(py-routingkit-app 
"main.cpp")

SET_TARGET_PROPERTIES(${PROJECT_NAME} PROPERTIES LINK_FLAGS "/PROFILE")

target_link_libraries(py-routingkit-app PRIVATE py-routingkit RoutingKit)