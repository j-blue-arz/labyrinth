import { state, getters, mutations } from "@/store/modules/board.js";
import { loc } from "../testutils.js";

describe("mutations", () => {
    describe("update", () => {
        it("sets maze size correctly", () => {
            givenInitialBoardState();
            givenApiStateWithSize3();

            whenSetBoardFromApi();

            expect(board.mazeSize).toEqual(3);
        });

        it("sets maze card id in 2d array correctly", () => {
            givenInitialBoardState();
            givenApiStateWithSize3();

            whenSetBoardFromApi();

            expect(getMazeCard(loc(1, 0))).toBe(7);
        });

        it("sets card by id correctly", () => {
            givenInitialBoardState();
            givenApiStateWithSize3();

            whenSetBoardFromApi();

            expect(board.cardsById["7"]).toEqual(
                expect.objectContaining({
                    outPaths: "NE",
                    id: 7,
                    location: {
                        column: 0,
                        row: 1
                    },
                    rotation: 180
                })
            );
        });

        it("sets leftover maze card id correctly", () => {
            givenInitialBoardState();
            givenApiStateWithSize3();

            whenSetBoardFromApi();

            expect(board.leftoverId).toBe(49);
        });

        it("disables shift location, if enabled locations is missing one", () => {
            givenInitialBoardState();
            givenApiStateWithSize3();

            whenSetBoardFromApi();

            expect(board.disabledShiftLocation).toEqual(loc(2, 1));
        });

        it("sets disabled shift location to null if all locations are enabled", () => {
            givenInitialBoardState();
            givenApiStateWithoutDisabledShiftLocations();

            whenSetBoardFromApi();

            expect(board.disabledShiftLocation).toEqual(null);
        });

        it("puts player ids on maze card", () => {
            givenInitialBoardState();
            givenApiStateWithSize3();

            whenSetBoardFromApi();
            const playerIds = board.cardsById["16"].playerIds;
            expect(Array.isArray(playerIds)).toBe(true);
            expect(new Set(playerIds)).toEqual(new Set([42, 17]));
            expect(playerIds.length).toBe(2);
        });

        it("leaves empty maze card player-ids empty", () => {
            givenInitialBoardState();
            givenApiStateWithSize3();

            whenSetBoardFromApi();
            expect(board.cardsById["2"].playerIds).toEqual([]);
        });
    });
});

const { update } = mutations;

let board;
let apiState;

const givenInitialBoardState = function() {
    board = state();
};

const givenApiStateWithSize3 = function() {
    apiState = JSON.parse(GET_STATE_RESULT_FOR_N_3);
};

const givenApiStateWithoutDisabledShiftLocations = function() {
    givenApiStateWithSize3();
    apiState.enabledShiftLocations.push(loc(2, 1));
};

const whenSetBoardFromApi = function() {
    update(board, apiState);
};

const getMazeCard = function(location) {
    return board.boardLayout[location.row][location.column];
};

const GET_STATE_RESULT_FOR_N_3 = `{
    "maze": {
      "mazeSize": 3,
      "mazeCards": [{
          "outPaths": "NES",
          "id": 49,
          "location": null,
          "rotation": 0
      }, {
          "outPaths": "NES",
          "id": 0,
          "location": {
          "column": 0,
          "row": 0
          },
          "rotation": 180
      }, {
          "outPaths": "NE",
          "id": 1,
          "location": {
          "column": 1,
          "row": 0
          },
          "rotation": 180
      }, {
          "outPaths": "NS",
          "id": 2,
          "location": {
          "column": 2,
          "row": 0
          },
          "rotation": 90
      }, {
          "outPaths": "NE",
          "id": 7,
          "location": {
          "column": 0,
          "row": 1
          },
          "rotation": 180
      }, {
          "outPaths": "NE",
          "id": 8,
          "location": {
          "column": 1,
          "row": 1
          },
          "rotation": 270
      }, {
          "outPaths": "NS",
          "id": 9,
          "location": {
          "column": 2,
          "row": 1
          },
          "rotation": 0
      }, {
          "outPaths": "NS",
          "id": 14,
          "location": {
          "column": 0,
          "row": 2
          },
          "rotation": 180
      }, {
          "outPaths": "NES",
          "id": 15,
          "location": {
          "column": 1,
          "row": 2
          },
          "rotation": 180
      }, {
          "outPaths": "NE",
          "id": 16,
          "location": {
          "column": 2,
          "row": 2
          },
          "rotation": 0
      }]
    },
    "enabledShiftLocations": [
      {"column": 1, "row": 0},
      {"column": 0, "row": 1},
      {"column": 2, "row": 1}
    ],
    "players": [{
            "id": 42,
            "mazeCardId": 16,
            "pieceIndex": 0
          },{
            "id": 17,
            "pieceIndex": 1,
            "mazeCardId": 16
          }]
  }`;