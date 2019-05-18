add_executable(benchmark "benchmark.cpp")
target_include_directories(benchmark PUBLIC ${PROJECT_SOURCE_DIR})
target_link_libraries(benchmark exhsearch BUILDER)
