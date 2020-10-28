set(
    TEST_SOURCES
        "util.h"
        "util.cpp"
        "solvers_test.h"
        "location_test.cpp"
        "maze_graph_test.cpp"
        "graph_algorithms_test.cpp"
        "graph_builder_test.cpp"
        "exhsearch_test.h"
        "exhsearch_test.cpp"
        "minimax_test.h"
        "minimax_test.cpp"
        "evaluators_test.cpp"
        "evaluators_test.h"
)

add_executable(all_tests ${TEST_SOURCES})
target_include_directories(all_tests PUBLIC ${PROJECT_SOURCE_DIR})
target_link_libraries(all_tests gtest gmock gtest_main exhsearch minimax BUILDER)
add_test(NAME all_tests COMMAND all_tests --gtest_output=xml:all_tests.xml)
set_target_properties(all_tests PROPERTIES FOLDER tests)
