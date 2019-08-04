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


if(COMPILE_TO_WASM)
	add_executable(libexhsearch ${SOURCES} extern.h extern.cpp)
    string(CONCAT EXHSEARCH_LINK_FLAGS "-g"
                             " -s WASM=1"
                             " -o libexhsearch.js"
                             " -s EXPORTED_FUNCTIONS='[_find_action]'")
    set_target_properties(libexhsearch PROPERTIES
            SUFFIX ".js"
            LINK_FLAGS ${EXHSEARCH_LINK_FLAGS})
elseif(NOT COMPILE_TO_WASM)
    add_library(exhsearch STATIC ${SOURCES})
    add_library(libexhsearch SHARED ${SOURCES} extern.h extern.cpp)
    install(TARGETS libexhsearch
        ARCHIVE DESTINATION lib/static
        RUNTIME DESTINATION bin)
endif(COMPILE_TO_WASM)


