add_executable(benchmark_exhsearch benchmark_exhsearch.cpp benchmark_reader.h)
target_include_directories(benchmark_exhsearch PUBLIC ${PROJECT_SOURCE_DIR})
target_link_libraries(benchmark_exhsearch exhsearch BUILDER stdc++fs)

add_executable(run_exhsearch run_exhsearch.cpp benchmark_reader.h)
target_include_directories(run_exhsearch PUBLIC ${PROJECT_SOURCE_DIR})
target_link_libraries(run_exhsearch exhsearch BUILDER stdc++fs)