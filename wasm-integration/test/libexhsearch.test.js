/**
 * @jest-environment node
 */
var libexhsearchLoader = require("../assets/libexhsearch");
var libexhsearch = null;

describe("libexhsearch", () => {
    beforeAll(async () => {
        var loader = libexhsearchLoader();
        loader.ready = () =>
            new Promise((resolve, reject) => {
                delete loader.then;
                loader.onAbort = reject;
                loader.addOnPostRun(() => {
                    resolve(loader);
                });
            });
        libexhsearch = await loader.ready();
    });

    test("findAction", async () => {
        const objectiveId = 7;
        const playerLocation = { row: 1, column: 2 };
        const previousShiftLocation = { row: 1, column: 0 };

        let outPaths = _outPathsForMaze(SMALL_MAZE);
        var vectorNodes = new libexhsearch.vectorOfNode();

        vectorNodes.push_back(new libexhsearch.Node(0, outPaths(0, 0), 0));
        vectorNodes.push_back(new libexhsearch.Node(1, outPaths(0, 1), 0));
        vectorNodes.push_back(new libexhsearch.Node(2, outPaths(0, 2), 0));
        vectorNodes.push_back(new libexhsearch.Node(3, outPaths(1, 0), 0));
        vectorNodes.push_back(new libexhsearch.Node(4, outPaths(1, 1), 0));
        vectorNodes.push_back(new libexhsearch.Node(5, outPaths(1, 2), 0));
        vectorNodes.push_back(new libexhsearch.Node(6, outPaths(2, 0), 0));
        vectorNodes.push_back(new libexhsearch.Node(7, outPaths(2, 1), 0));
        vectorNodes.push_back(new libexhsearch.Node(8, outPaths(2, 2), 0));
        vectorNodes.push_back(new libexhsearch.Node(9, 6, 0));

        let mazeGraph = new libexhsearch.MazeGraph(vectorNodes);
        mazeGraph.addShiftLocation({ row: 0, column: 1 });
        mazeGraph.addShiftLocation({ row: 1, column: 0 });
        mazeGraph.addShiftLocation({ row: 1, column: 2 });
        mazeGraph.addShiftLocation({ row: 2, column: 1 });

        let action = libexhsearch.findBestAction(
            mazeGraph,
            playerLocation,
            objectiveId,
            previousShiftLocation
        );
        expect(action).toMatchObject({
            shift: { location: { row: 2, column: 1 }, rotation: expect.any(Number) },
            move_location: { row: 1, column: 1 }
        });
        expect([0,90,180,270]).toContain(action.shift.rotation);

        mazeGraph.delete();
        for (let i = 0; i < vectorNodes.size(); ++i) {
            vectorNodes.get(i).delete();
        }
        vectorNodes.delete();
    });
});

function _getOutPathsBitmask(mazeStringArray, row, column) {
    let result = 0;
    row = row * 4;
    column = column * 4;
    if (mazeStringArray[row].charAt(column + 1) === ".") {
        result = result + 1;
    }
    if (mazeStringArray[row + 1].charAt(column + 2) === ".") {
        result = result + 2;
    }
    if (mazeStringArray[row + 2].charAt(column + 1) === ".") {
        result = result + 4;
    }
    if (mazeStringArray[row + 1].charAt(column) === ".") {
        result = result + 8;
    }
    return result;
}

function _outPathsForMaze(maze) {
    return function(row, column) {
        return _getOutPathsBitmask(maze, row, column);
    };
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
    "#..|#..|...|",
    "###|#.#|#.#|",
    "------------"
];
