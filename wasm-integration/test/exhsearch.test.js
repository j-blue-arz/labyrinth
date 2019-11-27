const fs = require("fs");
const path = require("path");

import { WasmMemory } from "@/assets/wrapper.js";
import { ExhsearchWrapper, Graph, MazeCard, Location } from "@/assets/exhsearch.js";

const TOTAL_MEMORY = 16 * 1024 * 1024; // 16 MB
const TOTAL_STACK = 5 * 1024 * 1024;

const wasmBinaryFile = "libexhsearch.wasm";


function _proc_exit(code) {
    if(code === 0) {
        return;
    } else {
        console.warn('program exited (with status: ' + status + ')');
    }
}

function error() {
    console.error('Operation now allowed');
    return 0;
}

describe("ExhsearchWrapper", () => {
    let exhsearch;
    let wasmMemory;

    beforeAll(async () => {
        const wasmPath = path.resolve(__dirname, "../assets", wasmBinaryFile);
        const buffer = fs.readFileSync(wasmPath);
        let wasmMemory = new WasmMemory();
        const result = await WebAssembly.instantiate(buffer, {
            // env: {
                // memoryBase: 0,
                // tableBase: 0,
                // table: new WebAssembly.Table({
                //     'initial': 27,
                //     'element': 'anyfunc'
                // }),
                // sbrk: wasmMemory.sbrk.bind(wasmMemory),
                // emscripten_memcpy_big: wasmMemory.memcpy_big.bind(wasmMemory),
                // memory: wasmMemory.memory,
                // abort: console.log
            // },
            wasi_unstable: {
                proc_exit: _proc_exit,
                fd_close: error,
                fd_write: error,
                fd_seek: error
            },
            env: {
                emscripten_notify_memory_growth: error //wasmMemory.updateBuffer
            }
        });
        const wasmInstance = result.instance;
        wasmMemory.setMemory(wasmInstance.exports.memory);
        exhsearch = new ExhsearchWrapper(wasmInstance, wasmMemory);
    });

    test("findAction", () => {
        const mazeCardMatrix = _buildMazeCardMatrix(SMALL_MAZE);
        const graph = new Graph(mazeCardMatrix.length, mazeCardMatrix, new MazeCard(9, "NS", 0));
        const objectiveId = mazeCardMatrix[0][2].id;
        const playerLocation = new Location(0, 2);
        const previousShiftLocation = new Location(1, 0);

        const action = exhsearch.findAction(graph, playerLocation, objectiveId, previousShiftLocation);
        console.log(action);
        expect(action).toMatchObject({
            shiftLocation: new Location(0, 1),
            rotation: expect.any(Number),
            moveLocation: new Location(0, 0)
        });
        expect([0,90,180,270]).toContain(action.rotation);
    });
});

function _getDoors(mazeStringArray, row, column) {
    let result = "";
    row = row * 4;
    column = column * 4;
    if(mazeStringArray[row].charAt(column + 1) === '.') {
        result = result.concat('N');
    }
    if(mazeStringArray[row+1].charAt(column + 2) === '.') {
        result = result.concat('E');
    }
    if(mazeStringArray[row+2].charAt(column + 1) === '.') {
        result = result.concat('S');
    }
    if(mazeStringArray[row+1].charAt(column) === '.') {
        result = result.concat('W');
    }
    return result;
}

function _buildMazeCardMatrix(mazeStringArray) {
    let mazeCards = [];
    let id = 0;
    const extent =  Math.floor(mazeStringArray.length / 4);
    for (let row = 0; row < extent; row++) {
        mazeCards.push([]);
        for (let col = 0; col < extent; col++) {
            mazeCards[row].push(new MazeCard(id, _getDoors(mazeStringArray, row, col), 0));
            id++;
        }
    }
    return mazeCards;
}

let SMALL_MAZE = [
    "###|###|#.#|",
    "#..|...|..#|",
    "#.#|#.#|###|",
    "------------",
    "#.#|###|###|",
    "#..|...|...|",
    "#.#|###|###|",
    "------------",
    "#.#|###|###|",
    "#..|#..|#..|",
    "###|#.#|#.#|",
    "------------"
]
