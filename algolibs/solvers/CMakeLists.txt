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

set (
    MINIMAX_SOURCES
        ${SOURCES}
        "minimax.h"
        "minimax.cpp"
        "evaluators.h"
        "evaluators.cpp"

)

set (
    EXHSEARCH_SOURCES
        ${SOURCES}
        "exhsearch.h"
        "exhsearch.cpp"
)

macro(add_libminimax_with_evaluator EVALUATOR_NAME LIBRARY_NAME)
    add_library(libminimax${LIBRARY_NAME} SHARED ${MINIMAX_SOURCES} c_api.h c_api_minimax.cpp)
    set_target_properties(libminimax${LIBRARY_NAME} PROPERTIES OUTPUT_NAME minimax${LIBRARY_NAME} COMPILE_DEFINITIONS ${EVALUATOR_NAME})
endmacro()

if(COMPILE_TO_WASM)
	add_executable(libexhsearch ${EXHSEARCH_SOURCES} wasm_api.cpp)
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
    add_library(exhsearch STATIC ${EXHSEARCH_SOURCES})
    set_target_properties(exhsearch PROPERTIES OUTPUT_NAME exhsearch)
    
    add_library(minimax STATIC ${MINIMAX_SOURCES})
    set_target_properties(minimax PROPERTIES OUTPUT_NAME minimax)

    add_library(libexhsearch SHARED ${EXHSEARCH_SOURCES} c_api.h c_api_exhsearch.cpp)
    set_target_properties(libexhsearch PROPERTIES OUTPUT_NAME exhsearch)

    add_libminimax_with_evaluator(MINIMAX_WIN_EVALUATOR "")
    #add_libminimax_with_evaluator(MINIMAX_REACHABLE_HEURISTIC -reachable)
    #add_libminimax_with_evaluator(MINIMAX_DISTANCE_HEURISTIC -distance)
endif(COMPILE_TO_WASM)


