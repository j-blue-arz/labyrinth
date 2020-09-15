add_executable(benchmark_exhsearch "benchmark_exhsearch.cpp")
target_include_directories(benchmark_exhsearch PUBLIC ${PROJECT_SOURCE_DIR})
target_link_libraries(benchmark_exhsearch exhsearch BUILDER stdc++fs)