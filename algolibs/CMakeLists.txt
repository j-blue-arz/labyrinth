cmake_minimum_required(VERSION 3.13)
set(PROJECT_VERSION "0.3.0")
project (algolibs VERSION ${PROJECT_VERSION} LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)

option(COMPILE_TO_WASM "Compiles to WebAssembly" OFF)

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

if(NOT COMPILE_TO_WASM)
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
    add_subdirectory(graphbuilder)
    add_subdirectory(benchmark)
endif(NOT COMPILE_TO_WASM)

add_subdirectory(solvers)

