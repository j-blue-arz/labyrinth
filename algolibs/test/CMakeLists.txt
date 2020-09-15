macro(package_add_test TESTNAME)
    add_executable(${TESTNAME} ${ARGN})
	target_include_directories(${TESTNAME} PUBLIC ${PROJECT_SOURCE_DIR})
    target_link_libraries(${TESTNAME} gtest gmock gtest_main exhsearch BUILDER)
    add_test(NAME ${TESTNAME} COMMAND ${TESTNAME} --gtest_output=xml:${TESTNAME}.xml)
    set_target_properties(${TESTNAME} PROPERTIES FOLDER tests)
endmacro()

set(
    TEST_SOURCES
        "util.h"
        "util.cpp"
        "mazes.h"
        "location_test.cpp"
        "maze_graph_test.cpp"
        "graph_algorithms_test.cpp"
        "graph_builder_test.cpp"
        "exhsearch_test.cpp"
)

add_executable(all_tests ${TEST_SOURCES})
target_include_directories(all_tests PUBLIC ${PROJECT_SOURCE_DIR})
target_link_libraries(all_tests gtest gmock gtest_main exhsearch BUILDER)
add_test(NAME all_tests COMMAND all_tests --gtest_output=xml:all_tests.xml)
set_target_properties(all_tests PROPERTIES FOLDER tests)

#package_add_test(location_test location_test.cpp)
#package_add_test(maze_graph_test maze_graph_test.cpp)
#package_add_test(graph_algorithms_test graph_algorithms_test.cpp)
#package_add_test(graph_builder_test graph_builder_test.cpp)
#package_add_test(exhsearch_test exhsearch_test.cpp)
