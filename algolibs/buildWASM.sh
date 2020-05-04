cd build
mkdir WASM
cd WASM
cmake ../.. -DCMAKE_TOOLCHAIN_FILE=~/emsdk/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake -DCOMPILE_TO_WASM=ON
make VERBOSE=1
~/emsdk/upstream/bin/wasm-dis libexhsearch/libexhsearch.wasm -o libexhsearch/libexhsearch.wast
cp libexhsearch/libexhsearch.js ../../../wasm-integration/assets/
cp libexhsearch/libexhsearch.wasm ../../../wasm-integration/assets/
