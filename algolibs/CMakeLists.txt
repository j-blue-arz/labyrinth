cmake_minimum_required(VERSION 3.13)
set(PROJECT_VERSION "0.1.3")
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

if(NOT COMPILE_TO_WASM)
    # Copied from https://github.com/google/googletest/tree/master/googletest
    # Download and unpack googletest at configure time
    configure_file(CMakeLists.txt.gtest googletest-download/CMakeLists.txt)
    execute_process(COMMAND ${CMAKE_COMMAND} -G "${CMAKE_GENERATOR}" .
        RESULT_VARIABLE result
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/googletest-download )
    if(result)
        message(FATAL_ERROR "CMake step for googletest failed: ${result}")
    endif()
    execute_process(COMMAND ${CMAKE_COMMAND} --build .
        RESULT_VARIABLE result
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/googletest-download )
    if(result)
        message(FATAL_ERROR "Build step for googletest failed: ${result}")
    endif()

    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)

    add_subdirectory(${CMAKE_CURRENT_BINARY_DIR}/googletest-src
                     ${CMAKE_CURRENT_BINARY_DIR}/googletest-build
                     EXCLUDE_FROM_ALL)

    enable_testing()
    add_subdirectory(test)
    add_subdirectory(graphbuilder)
    add_subdirectory(benchmark)
endif(NOT COMPILE_TO_WASM)

add_subdirectory(libexhsearch)

