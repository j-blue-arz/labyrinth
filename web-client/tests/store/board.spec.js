import boardConfig from "@/store/modules/board.js";
import { loc } from "../testutils.js";
import { createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";
import { cloneDeep } from "lodash";

describe("board Vuex module", () => {
    describe("actions", () => {
        // actions run against real store
        beforeEach(() => {
            const localVue = createLocalVue();
            localVue.use(Vuex);
            store = new Vuex.Store(cloneDeep(boardConfig));
        });

        describe("update", () => {
            it("sets maze size correctly", () => {
                givenApiStateWithSize3();

                whenSetBoardFromApi();

                thenBoardSizeIs(3);
            });

            it("sets maze card id in 2d array correctly", () => {
                givenApiStateWithSize3();

                whenSetBoardFromApi();

                expect(getMazeCard(loc(1, 0)).id).toBe(3);
            });

            it("sets card by id correctly", () => {
                givenApiStateWithSize3();

                whenSetBoardFromApi();

                expect(store.state.cardsById["3"]).toEqual(
                    expect.objectContaining({
                        outPaths: "NE",
                        id: 3,
                        location: {
                            column: 0,
                            row: 1,
                        },
                        rotation: 180,
                    })
                );
            });

            it("sets leftover maze card id correctly", () => {
                givenApiStateWithSize3();

                whenSetBoardFromApi();

                expect(store.getters.leftoverMazeCard.id).toBe(9);
            });

            it("disables shift location, if enabled locations is missing one", () => {
                givenApiStateWithSize3();

                whenSetBoardFromApi();

                expect(store.state.disabledShiftLocation).toEqual(loc(2, 1));
            });

            it("sets disabled shift location to null if all locations are enabled", () => {
                givenApiStateWithoutDisabledShiftLocations();

                whenSetBoardFromApi();

                expect(store.state.disabledShiftLocation).toEqual(null);
            });

            it("puts player ids on maze card", () => {
                givenApiStateWithSize3();

                whenSetBoardFromApi();

                const playerIds = store.getters.mazeCardById(2).playerIds;
                expect(Array.isArray(playerIds)).toBe(true);
                expect(new Set(playerIds)).toEqual(new Set([42, 17]));
                expect(playerIds.length).toBe(2);
            });

            it("removes player ids from maze card", () => {
                givenApiStateWithSize3();
                givenStoreFromApi();
                givenApiPlayerWithId(42).isOnMazeCard(3);
                givenApiPlayerWithId(17).isOnMazeCard(3);

                whenSetBoardFromApi();

                const playerIds = store.getters.mazeCardById(2).playerIds;
                expect(playerIds.length).toBe(0);
            });

            it("leaves empty maze card player ids empty", () => {
                givenApiStateWithSize3();

                whenSetBoardFromApi();

                expect(store.getters.mazeCardById(3).playerIds).toEqual([]);
            });

            it("overwrites existing state", () => {
                givenExistingBoardStateWithSize5();
                thenBoardSizeIs(5);
                givenApiStateWithSize3();

                whenSetBoardFromApi();

                thenBoardSizeIs(3);
                expect(store.state.boardLayout[0][0]).toEqual(0);
                expect(store.state.cardsById).not.toHaveProperty("100");
                expect(store.state.cardsById).toHaveProperty("1");
                expect(store.state.cardsById["8"].playerIds).toEqual([]);
            });
        });

        describe("move", () => {
            it("moves player to correct location", () => {
                givenStoreFromApi();

                whenMove({ sourceCardId: 2, targetCardId: 5, playerId: 42 });

                expect(playersOnCard(2)).not.toContain(42);
                expect(playersOnCard(5)).toContain(42);
            });
        });

        describe("shift", () => {
            it("updates disabled shift location", () => {
                givenStoreFromApi();

                whenShift(loc(1, 0), 90);

                expect(store.state.disabledShiftLocation).toEqual(loc(1, 2));
            });
        });

        describe("rotateLeftoverClockwise", () => {
            it("rotates leftover", () => {
                givenStoreFromApi();

                whenRotateLeftover();
                expect(store.getters.leftoverMazeCard.rotation).toEqual(90);
                whenRotateLeftover();
                expect(store.getters.leftoverMazeCard.rotation).toEqual(180);
                whenRotateLeftover();
                expect(store.getters.leftoverMazeCard.rotation).toEqual(270);
                whenRotateLeftover();
                expect(store.getters.leftoverMazeCard.rotation).toEqual(0);
            });
        });
    });

    describe("getters", () => {
        beforeEach(() => {
            const localVue = createLocalVue();
            localVue.use(Vuex);
            store = new Vuex.Store(cloneDeep(boardConfig));
        });

        describe("mazeCard", () => {
            it("returns the card for a given location", () => {
                givenStoreFromApi();

                const card = whenGetMazeCard({ column: 1, row: 1 });

                expect(card).toEqual(
                    expect.objectContaining({
                        location: { column: 1, row: 1 },
                    })
                );
            });

            it("throws RangeError on invalid location", () => {
                givenStoreFromApi();

                expect(() => whenGetMazeCard({ column: 7, row: 7 })).toThrow(RangeError);
            });
        });

        describe("mazeCardsRowMajorOrder", () => {
            it("returns 1d-array which contains all the board's maze cards", () => {
                givenStoreFromApi();

                const cards = whenGetMazeCardsRowMajorOrder();

                expect(cards.length).toBe(9);
                for (const [id, card] of Object.entries(store.state.cardsById)) {
                    if (parseInt(id) !== store.state.leftoverId) {
                        expect(cards).toContain(card);
                    }
                }
            });

            it("returns empty array for empty board", () => {
                const cards = whenGetMazeCardsRowMajorOrder();

                expect(cards).toBeInstanceOf(Array);
                expect(cards.length).toBe(0);
            });

            it("returns 1d-array with the game's maze cards ordered by row, then by column", () => {
                givenStoreFromApi();

                const cards = whenGetMazeCardsRowMajorOrder();

                let index = 0;
                for (let row = 0; row < 3; row++) {
                    for (let col = 0; col < 3; col++) {
                        expect(cards[index]).toBe(getMazeCard(loc(row, col)));
                        index++;
                    }
                }
            });
        });
    });
});

const { state } = boardConfig;

let store;
let board;
let apiState;

const givenExistingBoardStateWithSize5 = function () {
    board = state();
    board.mazeSize = 5;
    let id = 8;
    for (let row = 0; row < board.mazeSize; row++) {
        board.boardLayout.push([]);
        for (let col = 0; col < board.mazeSize; col++) {
            const card = {
                id: id,
                location: { row: row, column: col },
                rotation: 0,
                outPaths: "NES",
            };
            board.boardLayout[row].push(card.id);
            board.cardsById[card.id] = card;
            board.cardsById[card.id].playerIds = [];
            id++;
        }
    }
    board.cardsById[8].playerIds = [1, 2, 3, 4, 5];
    store.replaceState(cloneDeep(board));
};

const givenApiStateWithSize3 = function () {
    apiState = JSON.parse(GET_STATE_RESULT_FOR_N_3);
};

const givenApiStateWithoutDisabledShiftLocations = function () {
    givenApiStateWithSize3();
    apiState.enabledShiftLocations.push(loc(2, 1));
};

const givenStoreFromApi = function () {
    givenApiStateWithSize3();
    store.dispatch("update", apiState);
};

const givenApiPlayerWithId = function (playerId) {
    return {
        isOnMazeCard(cardId) {
            const player = apiState.players.find((player) => player.id === playerId);
            player.mazeCardId = cardId;
        },
    };
};

const whenSetBoardFromApi = function () {
    store.dispatch("update", apiState);
};

const whenMove = function (moveObject) {
    store.dispatch("movePlayer", moveObject);
};

const whenShift = function (location, rotation) {
    store.dispatch("shift", { location: location, leftoverRotation: rotation });
};

const whenGetMazeCard = function (location) {
    return getMazeCard(location);
};

const whenRotateLeftover = function () {
    store.dispatch("rotateLeftoverClockwise");
};

const whenGetMazeCardsRowMajorOrder = function () {
    return store.getters.mazeCardsRowMajorOrder;
};

const thenBoardSizeIs = function (size) {
    expect(store.state.mazeSize).toEqual(size);
    expect(store.state.boardLayout.length).toEqual(size);
    for (let row = 0; row < size; row++) {
        expect(store.state.boardLayout[row].length).toEqual(size);
    }
};

const getMazeCard = function (location) {
    return store.getters.mazeCard(location);
};

const playersOnCard = function (id) {
    return store.getters.mazeCardById(id).playerIds;
};

const GET_STATE_RESULT_FOR_N_3 = `{
    "maze": {
      "mazeSize": 3,
      "mazeCards": [{
          "outPaths": "NES",
          "id": 9,
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
          "id": 3,
          "location": {
          "column": 0,
          "row": 1
          },
          "rotation": 180
      }, {
          "outPaths": "NE",
          "id": 4,
          "location": {
          "column": 1,
          "row": 1
          },
          "rotation": 270
      }, {
          "outPaths": "NS",
          "id": 5,
          "location": {
          "column": 2,
          "row": 1
          },
          "rotation": 0
      }, {
          "outPaths": "NS",
          "id": 6,
          "location": {
          "column": 0,
          "row": 2
          },
          "rotation": 180
      }, {
          "outPaths": "NES",
          "id": 7,
          "location": {
          "column": 1,
          "row": 2
          },
          "rotation": 180
      }, {
          "outPaths": "NE",
          "id": 8,
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
            "mazeCardId": 2,
            "pieceIndex": 0
          },{
            "id": 17,
            "pieceIndex": 1,
            "mazeCardId": 2
          }]
  }`;
