cmake_minimum_required(VERSION 3.12)
set(PROJECT_VERSION "0.1.2")
project (algolibs VERSION ${PROJECT_VERSION} LANGUAGES CXX)

add_subdirectory(libexhsearch)
add_subdirectory(test)
