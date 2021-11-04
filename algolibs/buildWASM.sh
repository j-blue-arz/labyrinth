cd build
mkdir WASM
cd WASM
cmake ../.. -DCMAKE_TOOLCHAIN_FILE=~/emsdk/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake -DCOMPILE_TO_WASM=ON
make VERBOSE=1
cp solvers/libexhsearch.* ../../../web-client/public/wasm/
