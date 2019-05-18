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

add_library(exhsearch STATIC ${SOURCES})
add_library(libexhsearch SHARED ${SOURCES} extern.h extern.cpp)
install(TARGETS libexhsearch
            ARCHIVE DESTINATION lib/static
            RUNTIME DESTINATION bin)
