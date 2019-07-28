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
	add_executable(exhsearch ${SOURCES} extern.h extern.cpp)
	set(CMAKE_EXECUTABLE_SUFFIX ".js")
	set_target_properties(exhsearch PROPERTIES 
            LINK_FLAGS "-s WASM=1 -o exhsearch.js -s EXPORTED_FUNCTIONS='[_find_action]'")
elseif(NOT COMPILE_TO_WASM)
    add_library(exhsearch STATIC ${SOURCES})
    add_library(libexhsearch SHARED ${SOURCES} extern.h extern.cpp)
    install(TARGETS libexhsearch
        ARCHIVE DESTINATION lib/static
        RUNTIME DESTINATION bin)
endif(COMPILE_TO_WASM)


