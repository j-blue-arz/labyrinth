/**
 * @jest-environment node
 */
var libexhsearchLoader = require("../assets/libexhsearch");
var libexhsearch = null;

let STRAIGHT = [
    "#.#|###|#.#|###|", //
    "#.#|...|#.#|...|", //
    "#.#|###|#.#|###|",
];

let CORNER = [
    "#.#|###|###|#.#", //
    "#..|#..|..#|..#", //
    "###|#.#|#.#|###",
];

let T_JUNCT = [
    "#.#|###|#.#|#.#", //
    "#..|...|..#|...", //
    "#.#|#.#|#.#|###",
];

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
    "------------",
];

let GENERATED = [
    "###|#.#|###|#.#|###|###|###|",
    "#..|#.#|...|..#|...|...|..#|",
    "#.#|#.#|#.#|###|#.#|###|#.#|",
    "---------------------------|",
    "###|###|#.#|#.#|###|###|###|",
    "..#|...|#.#|..#|..#|...|#..|",
    "#.#|###|#.#|#.#|#.#|#.#|#.#|",
    "---------------------------|",
    "#.#|###|#.#|#.#|###|###|#.#|",
    "#..|...|#..|#.#|...|...|..#|",
    "#.#|###|#.#|#.#|#.#|###|#.#|",
    "---------------------------|",
    "#.#|###|#.#|#.#|###|#.#|###|",
    "#..|..#|#..|#..|...|#.#|...|",
    "#.#|#.#|###|###|#.#|#.#|###|",
    "---------------------------|",
    "#.#|###|#.#|###|#.#|###|#.#|",
    "#..|..#|...|..#|..#|..#|..#|",
    "#.#|#.#|###|#.#|#.#|#.#|#.#|",
    "---------------------------|",
    "#.#|#.#|###|#.#|###|###|###|",
    "#..|#..|..#|#..|..#|...|...|",
    "#.#|###|#.#|#.#|#.#|###|###|",
    "---------------------------|",
    "#.#|###|#.#|#.#|#.#|#.#|#.#|",
    "#..|..#|...|#..|...|#..|..#|",
    "###|#.#|###|###|###|#.#|###|",
    "----------------------------",
];

let DIFFICULT_MAZE = [
    "###|#.#|###|###|#.#|###|###|",
    "#..|#..|...|#..|#..|#..|..#|",
    "#.#|###|#.#|#.#|###|#.#|#.#|",
    "---------------------------|",
    "#.#|#.#|#.#|###|#.#|#.#|###|",
    "#..|..#|..#|...|#..|#.#|...|",
    "###|###|#.#|###|###|#.#|###|",
    "---------------------------|",
    "#.#|###|#.#|#.#|###|###|#.#|",
    "#..|#..|#..|#.#|...|...|..#|",
    "#.#|#.#|#.#|#.#|#.#|###|#.#|",
    "---------------------------|",
    "###|#.#|###|#.#|###|###|###|",
    "...|..#|#..|#.#|#..|...|...|",
    "###|#.#|#.#|#.#|#.#|###|###|",
    "---------------------------|",
    "#.#|#.#|#.#|#.#|#.#|###|#.#|",
    "#..|#..|#..|#.#|..#|...|...|",
    "#.#|###|#.#|#.#|#.#|###|###|",
    "---------------------------|",
    "###|#.#|#.#|#.#|#.#|#.#|#.#|",
    "..#|#..|#..|...|#.#|#..|..#|",
    "#.#|###|#.#|###|#.#|#.#|#.#|",
    "---------------------------|",
    "#.#|###|###|###|#.#|#.#|#.#|",
    "#..|...|#..|...|#.#|...|..#|",
    "###|###|#.#|###|#.#|###|###|",
    "----------------------------",
];

function _runTestScenario(testParameters) {
    let action = _computeActions(testParameters["setup"]);

    expect(action).toMatchObject(testParameters["expectedAction"]);
    expect(testParameters["possibleRotations"]).toContain(action.shift.rotation);
}

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

    test("api test for 3x3 matrix", async () => {
        _runTestScenario(test3x3);
    });

    test("depth 1 test for 7x7 matrix", async () => {
        _runTestScenario(test7x7_1);
    });

    test("depth 3 test for 7x7 matrix - 1", async () => {
        _runTestScenario(d3_generated_33s);
    });

    test("depth 3 test for 7x7 matrix - 2", async () => {
        _runTestScenario(d3_generated_23s);
    });

    test("depth 2 test which requires the player to be pushed out.", async () => {
        _runTestScenario(d2_self_push_out);
    });

    test("depth 1 test which requires the player to be pushed out.", async () => {
        _runTestScenario(d1_self_push_out);
    });

    test("let all scenarios run in one testcase", async () => {
        [test3x3, test7x7_1, d3_generated_33s, d3_generated_23s, d2_self_push_out].forEach(
            (testParameters) => {
                _runTestScenario(testParameters);
            }
        );
    });
});

let test3x3 = {
    setup: {
        mazeStringArray: SMALL_MAZE,
        leftOverStringArray: STRAIGHT,
        playerLocation: loc(1, 2),
        objectiveId: 7,
        previousShiftLocation: loc(1, 0),
    },
    expectedAction: {
        shift: { location: { row: 2, column: 1 }, rotation: expect.any(Number) },
        move_location: { row: 1, column: 1 },
    },
    possibleRotations: [0, 90, 180, 270],
};

let test7x7_1 = {
    setup: {
        mazeStringArray: GENERATED,
        leftOverStringArray: STRAIGHT,
        playerLocation: loc(0, 0),
        objectiveId: 44,
        previousShiftLocation: loc(0, 3),
    },
    expectedAction: {
        shift: { location: { row: 1, column: 0 }, rotation: expect.any(Number) },
        move_location: { row: 6, column: 2 },
    },
    possibleRotations: [0, 180],
};

let d3_generated_33s = {
    setup: {
        mazeStringArray: GENERATED,
        leftOverStringArray: STRAIGHT,
        playerLocation: loc(1, 4),
        objectiveId: 41,
        previousShiftLocation: loc(0, 3),
    },
    expectedAction: {
        shift: { location: { row: 1, column: 0 }, rotation: expect.any(Number) },
        move_location: { row: 1, column: 5 },
    },
    possibleRotations: [0],
};

let d3_generated_23s = {
    setup: {
        mazeStringArray: GENERATED,
        leftOverStringArray: STRAIGHT,
        playerLocation: loc(6, 6),
        objectiveId: 0,
        previousShiftLocation: loc(0, 3),
    },
    expectedAction: {
        shift: { location: { row: 0, column: 1 }, rotation: expect.any(Number) },
        move_location: { row: 6, column: 6 },
    },
    possibleRotations: [90, 270],
};

let d2_self_push_out = {
    setup: {
        mazeStringArray: DIFFICULT_MAZE,
        leftOverStringArray: CORNER,
        playerLocation: loc(0, 6),
        objectiveId: 48,
        previousShiftLocation: loc(0, 3),
    },
    expectedAction: {
        shift: { location: { row: 0, column: 1 }, rotation: expect.any(Number) },
        move_location: { row: 0, column: 5 },
    },
    possibleRotations: [0],
};

let d1_self_push_out = {
    setup: {
        mazeStringArray: GENERATED,
        leftOverStringArray: STRAIGHT,
        playerLocation: loc(6, 5),
        objectiveId: 6,
        previousShiftLocation: loc(3, 0),
    },
    expectedAction: {
        shift: { location: { row: 0, column: 5 }, rotation: expect.any(Number) },
        move_location: { row: 0, column: 6 },
    },
    possibleRotations: [90, 270],
};

function _computeActions(setup) {
    let mazeStringArray = setup["mazeStringArray"];
    let leftOverStringArray = setup["leftOverStringArray"];
    let playerLocation = setup["playerLocation"];
    let objectiveId = setup["objectiveId"];
    let previousShiftLocation = setup["previousShiftLocation"];
    const n = mazeStringArray.length / 4;
    let nodeFactory = _nodeFactory(mazeStringArray);
    var vectorNodes = new libexhsearch.vectorOfNode();
    let numNodes = n*n + 1;

    let idMapping = [];
    for(let i = 0; i < numNodes; i++) {
        idMapping.push(i);
    }
    shuffle(idMapping);

    let id = 0;
    for (let row = 0; row < n; row++) {
        for (let column = 0; column < n; column++) {
            let node = nodeFactory(row, column, idMapping[id]);
            vectorNodes.push_back(node);
            id++;
        }
    }
    let leftOverOuthPaths = _getBitmask(leftOverStringArray);
    vectorNodes.push_back(new libexhsearch.Node(idMapping[id], leftOverOuthPaths, 0));

    let mazeGraph = new libexhsearch.MazeGraph(vectorNodes);
    let border = n - 1;
    for (var position = 1; position < border; position += 2) {
        mazeGraph.addShiftLocation(loc(0, position));
        mazeGraph.addShiftLocation(loc(position, 0));
        mazeGraph.addShiftLocation(loc(position, border));
        mazeGraph.addShiftLocation(loc(border, position));
    }

    let action = libexhsearch.findBestAction(
        mazeGraph,
        playerLocation,
        idMapping[objectiveId],
        previousShiftLocation
    );

    mazeGraph.delete();
    for (let i = 0; i < vectorNodes.size(); ++i) {
        vectorNodes.get(i).delete();
    }
    vectorNodes.delete();

    return action;
}

function shuffle(array) {
    var currentIndex = array.length, temporaryValue, randomIndex;
  
    while (0 !== currentIndex) {
  
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex -= 1;
  
      temporaryValue = array[currentIndex];
      array[currentIndex] = array[randomIndex];
      array[randomIndex] = temporaryValue;
    }
  
    return array;
  }

function loc(row, column) {
    return { row: row, column: column };
}

function _nodeFactory(maze) {
    return function (row, column, id) {
        return _getNode(maze, row, column, id);
    };
}

function _getNode(mazeStringArray, row, column, id) {
    row = row * 4;
    column = column * 4;
    for (let pieceType of [STRAIGHT, CORNER, T_JUNCT]) {
        for (let rotation of [0, 1, 2, 3]) {
            let matches = true;
            for (let x = 0; x < 3; x++) {
                for (let y = 0; y < 3; y++) {
                    matches =
                        matches &&
                        mazeStringArray[row + y].charAt(column + x) ===
                            pieceType[y].charAt(rotation * 4 + x);
                }
            }
            if (matches) {
                return new libexhsearch.Node(id, _getBitmask(pieceType), rotation * 90);
            }
        }
    }
}

function _getBitmask(pieceType) {
    let result = 0;
    if (pieceType[0].charAt(1) === ".") {
        result = result + 1;
    }
    if (pieceType[1].charAt(2) === ".") {
        result = result + 2;
    }
    if (pieceType[2].charAt(1) === ".") {
        result = result + 4;
    }
    if (pieceType[1].charAt(0) === ".") {
        result = result + 8;
    }
    return result;
}
