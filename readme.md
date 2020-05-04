Labyrinth is a well-known german family board game. This project aims to recreate the game as a multiplayer game, develop understanding of the game's complexity and implement some computer opponents.

English manual to the game: https://www.ravensburger.com/spielanleitungen/ecm/Spielanleitungen/Labyrinth_26448_GB.pdf  
German manual to the game: https://www.ravensburger.de/spielanleitungen/ecm/Spielanleitungen/26446%20anl%201637944.pdf?ossl=pds_text_Spielanleitung

There is one major difference to the original game: all players have the same objective. 
The objective is always randomly chosen to be one of the 50 maze cards which is not occupied by a player's piece.

Also, it is only possible to reach an objective while making a move. Reaching an objective while it is another player's move is not counted.

# Quick start
Build the client and run the flask web server.
## Build web-client
    cd web-client
    npm install
    npm run test:unit
    npm run build

    cd ../backend

Now is a good time to create and activate a virtual environment, e.g. on Linux:

    python -m venv venv
    . venv/bin/activate

install required packages:

    pip install -r requirements.txt
    python -m pytest ./tests

## Running server  
Flask comes with a built-in server, which is perfectly fine for testing and developement of algorithms

    cd ../backend
    export FLASK_APP=server
    flask run --port=5000

Open localhost:5000 in your browser. Edge and IE are not supported.

If you want the server to be visible in your local network:

    flask run --host=0.0.0.0 --port=5000

## Benchmarks
    python -m benchmarking.bench_alpha_beta benchmark all

See the modules in backend/benchmarking for further instructions.

# Compiling algolibs
Algolibs contains C++ implementations of search algorithms, determining moves for a computer player. They are not required, but have better performance than
the python-based implementations shipped with the backend.
## Shared library
Requires cmake version 3.13 or newer. Tested with gcc 7.4.0. MSVC 14.23 works as well, but the library path is currently hard-coded in the python scripts, so you would have to change the respective path to get it to work.

    cd algolibs
    mkdir builds
    cmake -S. -Bbuilds/shared
    cmake --build builds/shared
    mkdir -p ../../../backend/lib/
    cp builds/shared/libexhsearch/libexhsearch.so ../backend/lib/

## WebAssembly
The repository contains a precompiled WebAssebmly binary and runtime. If you want to compile it yourself, you need the emsdk.

    cmake -S. -Bbuilds/wasm -DCMAKE_TOOLCHAIN_FILE=~/emsdk/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake -DCOMPILE_TO_WASM=ON
    cmake --build builds/wasm
    cp builds/wasm/libexhsearch/libexhsearch.js ../wasm-integration/assets/
    cp builds/wasm/libexhsearch/libexhsearch.wasm ../wasm-integration/assets/


