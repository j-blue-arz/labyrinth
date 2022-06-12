import Graph from "@/model/Graph";
import boardConfig, { loc } from "@/store/modules/board.js";
import { createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";
import { cloneDeep } from "lodash";

describe("Graph", () => {
    beforeEach(() => {
        const localVue = createLocalVue();
        localVue.use(Vuex);
        let store = new Vuex.Store(cloneDeep(boardConfig));
        const apiState = JSON.parse(GAME_STATE_GENERATED_WITH_LINE_LEFTOVER);
        store.dispatch("update", apiState);
        graph = new Graph(store.state);
    });

    describe("reachableLocations", () => {
        it("returns the source location for a component of size 1", () => {
            let reachable = graph.reachableLocations(loc(0, 0));

            expect(reachable.length).toBe(1);
            expect(reachable).toEqual(expect.arrayContaining([loc(0, 0)]));
        });

        it("finds all locations for a component of size 6 with cycle", () => {
            let reachable = graph.reachableLocations(loc(5, 3));

            expect(reachable.length).toBe(6);
            expect(reachable).toEqual(
                expect.arrayContaining([
                    loc(4, 2),
                    loc(4, 3),
                    loc(5, 3),
                    loc(5, 4),
                    loc(6, 3),
                    loc(6, 4),
                ])
            );
        });

        it("finds all locations for a component with outside connections to the north", () => {
            let reachable = graph.reachableLocations(loc(0, 2));

            expect(reachable.length).toBe(5);
            expect(reachable).toEqual(
                expect.arrayContaining([loc(0, 2), loc(0, 3), loc(1, 2), loc(2, 2), loc(3, 2)])
            );
        });

        it("finds all locations for a component with outside connections to the west and south", () => {
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
                    loc(6, 2),
                ])
            );
        });
    });

    describe("isReachable", () => {
        it("returns true for locations in same component", () => {
            expect(graph.isReachable(loc(0, 4), loc(0, 6))).toEqual(true);
        });

        it("returns false for locations in different components", () => {
            expect(graph.isReachable(loc(6, 0), loc(0, 6))).toEqual(false);
        });
    });
});

let graph;

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
    "maze": {
        "mazeSize": 7,
        "mazeCards": [{
        "outPaths": "NS",
        "id": 49,
        "location": null,
        "rotation": 270
        }, {
        "outPaths": "NE",
        "id": 0,
        "location": {
            "column": 0,
            "row": 0
        },
        "rotation": 90
        }, {
        "outPaths": "NS",
        "id": 1,
        "location": {
            "column": 1,
            "row": 0
        },
        "rotation": 180
        }, {
        "outPaths": "NES",
        "id": 2,
        "location": {
            "column": 2,
            "row": 0
        },
        "rotation": 90
        }, {
        "outPaths": "NE",
        "id": 3,
        "location": {
            "column": 3,
            "row": 0
        },
        "rotation": 270
        }, {
        "outPaths": "NES",
        "id": 4,
        "location": {
            "column": 4,
            "row": 0
        },
        "rotation": 90
        }, {
        "outPaths": "NS",
        "id": 5,
        "location": {
            "column": 5,
            "row": 0
        },
        "rotation": 90
        }, {
        "outPaths": "NE",
        "id": 6,
        "location": {
            "column": 6,
            "row": 0
        },
        "rotation": 180
        }, {
        "outPaths": "NE",
        "id": 7,
        "location": {
            "column": 0,
            "row": 1
        },
        "rotation": 180
        }, {
        "outPaths": "NS",
        "id": 8,
        "location": {
            "column": 1,
            "row": 1
        },
        "rotation": 90
        }, {
        "outPaths": "NS",
        "id": 9,
        "location": {
            "column": 2,
            "row": 1
        },
        "rotation": 180
        }, {
        "outPaths": "NES",
        "id": 10,
        "location": {
            "column": 3,
            "row": 1
        },
        "rotation": 180
        }, {
        "outPaths": "NE",
        "id": 11,
        "location": {
            "column": 4,
            "row": 1
        },
        "rotation": 180
        }, {
        "outPaths": "NES",
        "id": 12,
        "location": {
            "column": 5,
            "row": 1
        },
        "rotation": 90
        }, {
        "outPaths": "NE",
        "id": 13,
        "location": {
            "column": 6,
            "row": 1
        },
        "rotation": 90
        }, {
        "outPaths": "NES",
        "id": 14,
        "location": {
            "column": 0,
            "row": 2
        },
        "rotation": 0
        }, {
        "outPaths": "NS",
        "id": 15,
        "location": {
            "column": 1,
            "row": 2
        },
        "rotation": 90
        }, {
        "outPaths": "NES",
        "id": 16,
        "location": {
            "column": 2,
            "row": 2
        },
        "rotation": 0
        }, {
        "outPaths": "NS",
        "id": 17,
        "location": {
            "column": 3,
            "row": 2
        },
        "rotation": 180
        }, {
        "outPaths": "NES",
        "id": 18,
        "location": {
            "column": 4,
            "row": 2
        },
        "rotation": 90
        }, {
        "outPaths": "NS",
        "id": 19,
        "location": {
            "column": 5,
            "row": 2
        },
        "rotation": 90
        }, {
        "outPaths": "NES",
        "id": 20,
        "location": {
            "column": 6,
            "row": 2
        },
        "rotation": 180
        }, {
        "outPaths": "NES",
        "id": 21,
        "location": {
            "column": 0,
            "row": 3
        },
        "rotation": 0
        }, {
        "outPaths": "NE",
        "id": 22,
        "location": {
            "column": 1,
            "row": 3
        },
        "rotation": 180
        }, {
        "outPaths": "NE",
        "id": 23,
        "location": {
            "column": 2,
            "row": 3
        },
        "rotation": 0
        }, {
        "outPaths": "NE",
        "id": 24,
        "location": {
            "column": 3,
            "row": 3
        },
        "rotation": 0
        }, {
        "outPaths": "NES",
        "id": 25,
        "location": {
            "column": 4,
            "row": 3
        },
        "rotation": 90
        }, {
        "outPaths": "NS",
        "id": 26,
        "location": {
            "column": 5,
            "row": 3
        },
        "rotation": 180
        }, {
        "outPaths": "NS",
        "id": 27,
        "location": {
            "column": 6,
            "row": 3
        },
        "rotation": 90
        }, {
        "outPaths": "NES",
        "id": 28,
        "location": {
            "column": 0,
            "row": 4
        },
        "rotation": 0
        }, {
        "outPaths": "NE",
        "id": 29,
        "location": {
            "column": 1,
            "row": 4
        },
        "rotation": 180
        }, {
        "outPaths": "NES",
        "id": 30,
        "location": {
            "column": 2,
            "row": 4
        },
        "rotation": 270
        }, {
        "outPaths": "NE",
        "id": 31,
        "location": {
            "column": 3,
            "row": 4
        },
        "rotation": 180
        }, {
        "outPaths": "NES",
        "id": 32,
        "location": {
            "column": 4,
            "row": 4
        },
        "rotation": 180
        }, {
        "outPaths": "NE",
        "id": 33,
        "location": {
            "column": 5,
            "row": 4
        },
        "rotation": 180
        }, {
        "outPaths": "NES",
        "id": 34,
        "location": {
            "column": 6,
            "row": 4
        },
        "rotation": 180
        }, {
        "outPaths": "NES",
        "id": 35,
        "location": {
            "column": 0,
            "row": 5
        },
        "rotation": 0
        }, {
        "outPaths": "NE",
        "id": 36,
        "location": {
            "column": 1,
            "row": 5
        },
        "rotation": 0
        }, {
        "outPaths": "NE",
        "id": 37,
        "location": {
            "column": 2,
            "row": 5
        },
        "rotation": 180
        }, {
        "outPaths": "NES",
        "id": 38,
        "location": {
            "column": 3,
            "row": 5
        },
        "rotation": 0
        }, {
        "outPaths": "NE",
        "id": 39,
        "location": {
            "column": 4,
            "row": 5
        },
        "rotation": 180
        }, {
        "outPaths": "NS",
        "id": 40,
        "location": {
            "column": 5,
            "row": 5
        },
        "rotation": 90
        }, {
        "outPaths": "NS",
        "id": 41,
        "location": {
            "column": 6,
            "row": 5
        },
        "rotation": 90
        }, {
        "outPaths": "NE",
        "id": 42,
        "location": {
            "column": 0,
            "row": 6
        },
        "rotation": 0
        }, {
        "outPaths": "NE",
        "id": 43,
        "location": {
            "column": 1,
            "row": 6
        },
        "rotation": 180
        }, {
        "outPaths": "NES",
        "id": 44,
        "location": {
            "column": 2,
            "row": 6
        },
        "rotation": 270
        }, {
        "outPaths": "NE",
        "id": 45,
        "location": {
            "column": 3,
            "row": 6
        },
        "rotation": 0
        }, {
        "outPaths": "NES",
        "id": 46,
        "location": {
            "column": 4,
            "row": 6
        },
        "rotation": 270
        }, {
        "outPaths": "NES",
        "id": 47,
        "location": {
            "column": 5,
            "row": 6
        },
        "rotation": 0
        }, {
        "outPaths": "NE",
        "id": 48,
        "location": {
            "column": 6,
            "row": 6
        },
        "rotation": 270
        }]
    },
    "players": [{
      "id": 1,
      "isBot": false,
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
