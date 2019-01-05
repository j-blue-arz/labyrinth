import Game from "@/model/game";
import Graph from "@/model/mazeAlgorithm";
import { loc } from "./testutils.js";

describe("Graph", () => {
    describe("reachableLocations", () => {
        it("returns the source location for a component of size 1", () => {
            let game = new Game();
            game.createFromApi(
                JSON.parse(GAME_STATE_GENERATED_WITH_LINE_LEFTOVER)
            );
            let graph = new Graph(game);
            let reachable = graph.reachableLocations(loc(0, 0));

            expect(reachable.length).toBe(1);
            expect(reachable).toEqual(expect.arrayContaining([loc(0, 0)]));
        });

        it("finds all locations for a component of size 6 with cycle", () => {
            let game = new Game();
            game.createFromApi(
                JSON.parse(GAME_STATE_GENERATED_WITH_LINE_LEFTOVER)
            );
            let graph = new Graph(game);
            let reachable = graph.reachableLocations(loc(5, 3));

            expect(reachable.length).toBe(6);
            expect(reachable).toEqual(
                expect.arrayContaining([
                    loc(4, 2),
                    loc(4, 3),
                    loc(5, 3),
                    loc(5, 4),
                    loc(6, 3),
                    loc(6, 4)
                ])
            );
        });

        it("finds all locations for a component with outside connections to the north", () => {
            let game = new Game();
            game.createFromApi(
                JSON.parse(GAME_STATE_GENERATED_WITH_LINE_LEFTOVER)
            );
            let graph = new Graph(game);
            let reachable = graph.reachableLocations(loc(0, 2));

            expect(reachable.length).toBe(5);
            expect(reachable).toEqual(
                expect.arrayContaining([
                    loc(0, 2),
                    loc(0, 3),
                    loc(1, 2),
                    loc(2, 2),
                    loc(3, 2)
                ])
            );
        });

        it("finds all locations for a component with outside connections to the west and south", () => {
            let game = new Game();
            game.createFromApi(
                JSON.parse(GAME_STATE_GENERATED_WITH_LINE_LEFTOVER)
            );
            let graph = new Graph(game);
            let reachable = graph.reachableLocations(loc(6, 2));

            expect(reachable.length).toBe(13);
            expect(reachable).toEqual(
                expect.arrayContaining([
                    loc(1, 0),
                    loc(2, 0),
                    loc(3, 0),
                    loc(4, 0),
                    loc(5, 0),
                    loc(6, 0),
                    loc(2, 1),
                    loc(3, 1),
                    loc(4, 1),
                    loc(5, 1),
                    loc(6, 1),
                    loc(5, 2),
                    loc(6, 2)
                ])
            );
        });
    });

    describe("isReachable", () => {
        it("returns true for locations in same component", () => {
            let game = new Game();
            game.createFromApi(
                JSON.parse(GAME_STATE_GENERATED_WITH_LINE_LEFTOVER)
            );
            let graph = new Graph(game);

            expect(graph.isReachable(loc(0, 4), loc(0, 6))).toEqual(true);
        });

        it("returns false for locations in different components", () => {
            let game = new Game();
            game.createFromApi(
                JSON.parse(GAME_STATE_GENERATED_WITH_LINE_LEFTOVER)
            );
            let graph = new Graph(game);

            expect(graph.isReachable(loc(6, 0), loc(0, 6))).toEqual(false);
        });
    });
});

/* GENERATED_WITH_LINE_LEFTOVER =
###|#.#|###|#.#|###|###|###|
#..|#.#|...|..#|...|...|..#|
#.#|#.#|#.#|###|#.#|###|#.#|
---------------------------|
###|###|#.#|#.#|###|###|###|
..#|...|#.#|..#|..#|...|#..|
#.#|###|#.#|#.#|#.#|#.#|#.#|
---------------------------|
#.#|###|#.#|#.#|###|###|#.#|
#..|...|#..|#.#|...|...|..#|
#.#|###|#.#|#.#|#.#|###|#.#|
---------------------------|
#.#|###|#.#|#.#|###|#.#|###|
#..|..#|#..|#..|...|#.#|...|
#.#|#.#|###|###|#.#|#.#|###|
---------------------------|
#.#|###|#.#|###|#.#|###|#.#|
#..|..#|...|..#|..#|..#|..#|
#.#|#.#|###|#.#|#.#|#.#|#.#|
---------------------------|
#.#|#.#|###|#.#|###|###|###|
#..|#..|..#|#..|..#|...|...|
#.#|###|#.#|#.#|#.#|###|###|
---------------------------|
#.#|###|#.#|#.#|#.#|#.#|#.#|
#..|..#|...|#..|...|#..|..#|
###|#.#|###|###|###|#.#|###|
---------------------------* */

let GAME_STATE_GENERATED_WITH_LINE_LEFTOVER = `{
    "mazeCards": [{
      "doors": "NS",
      "id": 49,
      "location": null,
      "rotation": 270
    }, {
      "doors": "NE",
      "id": 0,
      "location": {
        "column": 0,
        "row": 0
      },
      "rotation": 90
    }, {
      "doors": "NS",
      "id": 1,
      "location": {
        "column": 1,
        "row": 0
      },
      "rotation": 180
    }, {
      "doors": "NES",
      "id": 2,
      "location": {
        "column": 2,
        "row": 0
      },
      "rotation": 90
    }, {
      "doors": "NE",
      "id": 3,
      "location": {
        "column": 3,
        "row": 0
      },
      "rotation": 270
    }, {
      "doors": "NES",
      "id": 4,
      "location": {
        "column": 4,
        "row": 0
      },
      "rotation": 90
    }, {
      "doors": "NS",
      "id": 5,
      "location": {
        "column": 5,
        "row": 0
      },
      "rotation": 90
    }, {
      "doors": "NE",
      "id": 6,
      "location": {
        "column": 6,
        "row": 0
      },
      "rotation": 180
    }, {
      "doors": "NE",
      "id": 7,
      "location": {
        "column": 0,
        "row": 1
      },
      "rotation": 180
    }, {
      "doors": "NS",
      "id": 8,
      "location": {
        "column": 1,
        "row": 1
      },
      "rotation": 90
    }, {
      "doors": "NS",
      "id": 9,
      "location": {
        "column": 2,
        "row": 1
      },
      "rotation": 180
    }, {
      "doors": "NES",
      "id": 10,
      "location": {
        "column": 3,
        "row": 1
      },
      "rotation": 180
    }, {
      "doors": "NE",
      "id": 11,
      "location": {
        "column": 4,
        "row": 1
      },
      "rotation": 180
    }, {
      "doors": "NES",
      "id": 12,
      "location": {
        "column": 5,
        "row": 1
      },
      "rotation": 90
    }, {
      "doors": "NE",
      "id": 13,
      "location": {
        "column": 6,
        "row": 1
      },
      "rotation": 90
    }, {
      "doors": "NES",
      "id": 14,
      "location": {
        "column": 0,
        "row": 2
      },
      "rotation": 0
    }, {
      "doors": "NS",
      "id": 15,
      "location": {
        "column": 1,
        "row": 2
      },
      "rotation": 90
    }, {
      "doors": "NES",
      "id": 16,
      "location": {
        "column": 2,
        "row": 2
      },
      "rotation": 0
    }, {
      "doors": "NS",
      "id": 17,
      "location": {
        "column": 3,
        "row": 2
      },
      "rotation": 180
    }, {
      "doors": "NES",
      "id": 18,
      "location": {
        "column": 4,
        "row": 2
      },
      "rotation": 90
    }, {
      "doors": "NS",
      "id": 19,
      "location": {
        "column": 5,
        "row": 2
      },
      "rotation": 90
    }, {
      "doors": "NES",
      "id": 20,
      "location": {
        "column": 6,
        "row": 2
      },
      "rotation": 180
    }, {
      "doors": "NES",
      "id": 21,
      "location": {
        "column": 0,
        "row": 3
      },
      "rotation": 0
    }, {
      "doors": "NE",
      "id": 22,
      "location": {
        "column": 1,
        "row": 3
      },
      "rotation": 180
    }, {
      "doors": "NE",
      "id": 23,
      "location": {
        "column": 2,
        "row": 3
      },
      "rotation": 0
    }, {
      "doors": "NE",
      "id": 24,
      "location": {
        "column": 3,
        "row": 3
      },
      "rotation": 0
    }, {
      "doors": "NES",
      "id": 25,
      "location": {
        "column": 4,
        "row": 3
      },
      "rotation": 90
    }, {
      "doors": "NS",
      "id": 26,
      "location": {
        "column": 5,
        "row": 3
      },
      "rotation": 180
    }, {
      "doors": "NS",
      "id": 27,
      "location": {
        "column": 6,
        "row": 3
      },
      "rotation": 90
    }, {
      "doors": "NES",
      "id": 28,
      "location": {
        "column": 0,
        "row": 4
      },
      "rotation": 0
    }, {
      "doors": "NE",
      "id": 29,
      "location": {
        "column": 1,
        "row": 4
      },
      "rotation": 180
    }, {
      "doors": "NES",
      "id": 30,
      "location": {
        "column": 2,
        "row": 4
      },
      "rotation": 270
    }, {
      "doors": "NE",
      "id": 31,
      "location": {
        "column": 3,
        "row": 4
      },
      "rotation": 180
    }, {
      "doors": "NES",
      "id": 32,
      "location": {
        "column": 4,
        "row": 4
      },
      "rotation": 180
    }, {
      "doors": "NE",
      "id": 33,
      "location": {
        "column": 5,
        "row": 4
      },
      "rotation": 180
    }, {
      "doors": "NES",
      "id": 34,
      "location": {
        "column": 6,
        "row": 4
      },
      "rotation": 180
    }, {
      "doors": "NES",
      "id": 35,
      "location": {
        "column": 0,
        "row": 5
      },
      "rotation": 0
    }, {
      "doors": "NE",
      "id": 36,
      "location": {
        "column": 1,
        "row": 5
      },
      "rotation": 0
    }, {
      "doors": "NE",
      "id": 37,
      "location": {
        "column": 2,
        "row": 5
      },
      "rotation": 180
    }, {
      "doors": "NES",
      "id": 38,
      "location": {
        "column": 3,
        "row": 5
      },
      "rotation": 0
    }, {
      "doors": "NE",
      "id": 39,
      "location": {
        "column": 4,
        "row": 5
      },
      "rotation": 180
    }, {
      "doors": "NS",
      "id": 40,
      "location": {
        "column": 5,
        "row": 5
      },
      "rotation": 90
    }, {
      "doors": "NS",
      "id": 41,
      "location": {
        "column": 6,
        "row": 5
      },
      "rotation": 90
    }, {
      "doors": "NE",
      "id": 42,
      "location": {
        "column": 0,
        "row": 6
      },
      "rotation": 0
    }, {
      "doors": "NE",
      "id": 43,
      "location": {
        "column": 1,
        "row": 6
      },
      "rotation": 180
    }, {
      "doors": "NES",
      "id": 44,
      "location": {
        "column": 2,
        "row": 6
      },
      "rotation": 270
    }, {
      "doors": "NE",
      "id": 45,
      "location": {
        "column": 3,
        "row": 6
      },
      "rotation": 0
    }, {
      "doors": "NES",
      "id": 46,
      "location": {
        "column": 4,
        "row": 6
      },
      "rotation": 270
    }, {
      "doors": "NES",
      "id": 47,
      "location": {
        "column": 5,
        "row": 6
      },
      "rotation": 0
    }, {
      "doors": "NE",
      "id": 48,
      "location": {
        "column": 6,
        "row": 6
      },
      "rotation": 270
    }],
    "nextAction": {
      "action": "MOVE",
      "playerId": 1
    },
    "objectiveMazeCardId": 34,
    "players": [{
      "id": 1,
      "isComputerPlayer": false,
      "mazeCardId": 0
    }],
    "enabledShiftLocations": [
        {
          "column": 0,
          "row": 3
        },
        {
          "column": 6,
          "row": 5
        },
        {
          "column": 6,
          "row": 1
        },
        {
          "column": 5,
          "row": 0
        },
        {
          "column": 0,
          "row": 1
        },
        {
          "column": 3,
          "row": 0
        },
        {
          "column": 5,
          "row": 6
        },
        {
          "column": 1,
          "row": 0
        },
        {
          "column": 1,
          "row": 6
        },
        {
          "column": 3,
          "row": 6
        },
        {
          "column": 6,
          "row": 3
        },
        {
          "column": 0,
          "row": 5
        }
      ]
  }`;
