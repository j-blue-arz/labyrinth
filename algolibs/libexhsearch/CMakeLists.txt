set(
    SOURCES 
		"graph_builder.h"
		"graph_builder.cpp"
		"graph_algorithms.h"
		"graph_algorithms.cpp"
		"location.h"
		"location.cpp"
		"static_graph.h"
		"static_graph.cpp"
)

add_library(REACHABLE OBJECT ${SOURCES})

add_executable(benchmark "benchmark.cpp" ${SOURCES})

add_executable(run "run.cpp" ${SOURCES})
