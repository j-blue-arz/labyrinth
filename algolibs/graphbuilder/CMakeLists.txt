if(TARGET BUILDER)
    return()
endif(TARGET BUILDER)

set(
    SOURCES 
		"graph_builder.h"
		"graph_builder.cpp"
		"text_graph_builder.h"
		"text_graph_builder.cpp"
)

add_library(BUILDER ${SOURCES})
target_include_directories(BUILDER PUBLIC ${PROJECT_SOURCE_DIR})
target_link_libraries(BUILDER exhsearch)
