cmake_minimum_required(VERSION 3.13)
set(PROJECT_VERSION "0.3.0")
project (algolibs VERSION ${PROJECT_VERSION} LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)

# options: building wasm is only possible when building solvers, and will deactivate build of tests and benchmarks.
include(CMakeDependentOption)
option(BUILD_SOLVERS "Will build the solvers as libraries or wasm." ON)
cmake_dependent_option(COMPILE_TO_WASM "Compiles to WebAssembly. This will only build the solvers to .wasm, and omit tests and benchmarks." OFF
                       "BUILD_SOLVERS" OFF)
cmake_dependent_option(BUILD_TESTS "Will build the tests. This might take a while due to gtest download." ON
                       "NOT COMPILE_TO_WASM" OFF)
cmake_dependent_option(BUILD_BENCHMARKS "Will build the benchmarks." ON
                       "NOT COMPILE_TO_WASM" OFF)


if (MSVC)
    # warning level 4 - requires to replace compiler option, because cmake sets /W3 by default
	# Inspired by https://github.com/google/googletest/blob/master/googletest/cmake/internal_utils.cmake
	foreach (flag_var CMAKE_C_FLAGS CMAKE_CXX_FLAGS )
		string(REPLACE "/W3" "/W4" ${flag_var} "${${flag_var}}")
	endforeach()
else()
    # lots of warnings
    add_compile_options(-Wall -Wextra)
endif()

# always debug info
if(MSVC)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /Zi")
else()
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g")
endif()

if(BUILD_TESTS)
    include(FetchContent)
    FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG        master
    )
    FetchContent_GetProperties(googletest)
    if(NOT googletest_POPULATED)
        FetchContent_Populate(googletest)
        add_subdirectory(${googletest_SOURCE_DIR} ${googletest_BINARY_DIR})
    endif()

    enable_testing()
    add_subdirectory(test)
endif(BUILD_TESTS)

if(BUILD_BENCHMARKS)
    add_subdirectory(benchmark)
endif(BUILD_BENCHMARKS)

if(BUILD_TESTS OR BUILD_BENCHMARKS)
    add_subdirectory(graphbuilder)
endif(BUILD_TESTS OR BUILD_BENCHMARKS)

if(BUILD_SOLVERS OR COMPILE_TO_WASM OR BUILD_TESTS)
    add_subdirectory(solvers)
endif(BUILD_SOLVERS OR COMPILE_TO_WASM OR BUILD_TESTS)

