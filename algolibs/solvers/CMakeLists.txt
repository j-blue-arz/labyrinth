set(
    SOURCES
		"graph_algorithms.h"
		"graph_algorithms.cpp"
		"location.h"
		"location.cpp"
		"maze_graph.h"
		"maze_graph.cpp"
        "solvers.h"
        "solvers.cpp"
)


if(COMPILE_TO_WASM)
	add_executable(libexhsearch ${SOURCES} exhsearch.h exhsearch.cpp wasm_api.cpp)
    string(CONCAT EXHSEARCH_LINK_FLAGS
                             " -s WASM=1"
                             " -o libexhsearch.js"
                             " -s ALLOW_MEMORY_GROWTH=1"
                             " -s MODULARIZE=1"
                             " -s EXPORT_NAME=libexhsearch"
                             " -s \"EXTRA_EXPORTED_RUNTIME_METHODS=['addOnPostRun']\""
                             " --bind")
    set_target_properties(libexhsearch PROPERTIES
            SUFFIX ".js"
            LINK_FLAGS ${EXHSEARCH_LINK_FLAGS}
            COMPILE_FLAGS " -fno-exceptions")
elseif(NOT COMPILE_TO_WASM)
    add_library(exhsearch STATIC ${SOURCES} exhsearch.h exhsearch.cpp)
    set_target_properties(exhsearch PROPERTIES OUTPUT_NAME exhsearch)
    add_library(libexhsearch SHARED ${SOURCES} exhsearch.h exhsearch.cpp c_api.h c_api_exhsearch.cpp)
    set_target_properties(libexhsearch PROPERTIES OUTPUT_NAME exhsearch)
    
    add_library(minimax STATIC ${SOURCES} minimax.h minimax.cpp)
    set_target_properties(minimax PROPERTIES OUTPUT_NAME minimax)
    add_library(libminimax SHARED ${SOURCES} minimax.h minimax.cpp c_api.h c_api_minimax.cpp)
    set_target_properties(libminimax PROPERTIES OUTPUT_NAME minimax)
endif(COMPILE_TO_WASM)


