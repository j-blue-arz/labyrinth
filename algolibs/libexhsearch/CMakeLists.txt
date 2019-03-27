set(
    SOURCES 
		"graph_algorithms.h"
		"graph_algorithms.cpp"
		"location.h"
		"location.cpp"
		"static_graph.h"
		"static_graph.cpp"
)

add_library(REACHABLE OBJECT ${SOURCES})
