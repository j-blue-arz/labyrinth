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
	add_executable(libexhsearch ${SOURCES} wasm_api.cpp)
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
    add_library(exhsearch STATIC ${SOURCES})
    set_target_properties(exhsearch PROPERTIES OUTPUT_NAME exhsearch)
    add_library(libexhsearch SHARED ${SOURCES} c_api.h c_api.cpp)
    set_target_properties(libexhsearch PROPERTIES OUTPUT_NAME exhsearch)
    install(TARGETS libexhsearch
        ARCHIVE DESTINATION lib/static
        RUNTIME DESTINATION bin)
endif(COMPILE_TO_WASM)


