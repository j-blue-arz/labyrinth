set(
    SOURCES 
		"graph_algorithms.h"
		"graph_algorithms.cpp"
		"location.h"
		"location.cpp"
		"maze_graph.h"
		"maze_graph.cpp"
		"exhsearch.h"
		"exhsearch.cpp"
)

add_library(REACHABLE OBJECT ${SOURCES})
