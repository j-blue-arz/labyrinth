# Overview
This folder contains implementations of search algorithms which are used by bots playing the game.
There are currently two algorithms:
* *Exhaustive search* finds the minimum number of actions to reach the objective, assuming there is only one player.
* *Minimax* is a two-player implementation of the minimax algorithm. Two heuristics are implemented: one minimizing the *distance* to the objective, another maximizing the *reachable* maze cards.

# Building
## Shared library
Requires cmake version 3.13 or newer. Tested with gcc 8.4.0. The backend application loads .dll files on Windows, and .so files everywhere else.

    cd algolibs
    mkdir -p build/shared
    cmake -S. -Bbuild/shared
    cmake --build build/shared
    mkdir -p ../backend/instance/lib/
    cp build/shared/solvers/*.so ../backend/instance/lib/

## WebAssembly
The repository contains a precompiled WebAssembly binary and runtime. If you want to compile it yourself, you need the emsdk.

    cmake -S. -Bbuild/wasm -DCMAKE_TOOLCHAIN_FILE=~/emsdk/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake -DCOMPILE_TO_WASM=ON
    cmake --build build/wasm
    cp build/wasm/libexhsearch/libexhsearch.js ../backend/static/wasm/
    cp build/wasm/libexhsearch/libexhsearch.wasm ../backend/static/wasm/

The distribution folder is overwritten if you build the web-client. To keep your versions of the WebAssembly files, put them in 

    web-client/public/wasm/