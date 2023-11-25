import { stateFactory, useBoardStore } from "@/stores/board.js";
import { cloneDeep } from "lodash";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it } from "vitest";

describe("Board Store", () => {
    describe("actions", () => {
        beforeEach(() => {
            setActivePinia(createPinia());
            boardStore = useBoardStore();
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

                expect(boardStore.cardsById["3"]).toEqual(
                    expect.objectContaining({
                        outPaths: "NE",
                        id: 3,
                        location: {
                            column: 0,
                            row: 1,
                        },
                        rotation: 180,
                    }),
                );
            });

            it("sets leftover maze card id correctly", () => {
                givenApiStateWithSize3();

                whenSetBoardFromApi();

                expect(boardStore.leftoverMazeCard.id).toBe(9);
            });

            it("disables shift location, if enabled locations is missing one", () => {
                givenApiStateWithSize3();

                whenSetBoardFromApi();

                expect(boardStore.disabledShiftLocation).toEqual(loc(2, 1));
            });

            it("sets disabled shift location to null if all locations are enabled", () => {
                givenApiStateWithoutDisabledShiftLocations();

                whenSetBoardFromApi();

                expect(boardStore.disabledShiftLocation).toEqual(null);
            });

            it("puts player ids on maze card", () => {
                givenApiStateWithSize3();

                whenSetBoardFromApi();

                const playerIds = boardStore.mazeCardById(2).playerIds;
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

                const playerIds = boardStore.mazeCardById(2).playerIds;
                expect(playerIds.length).toBe(0);
            });

            it("leaves empty maze card player ids empty", () => {
                givenApiStateWithSize3();

                whenSetBoardFromApi();

                expect(boardStore.mazeCardById(3).playerIds).toEqual([]);
            });

            it("overwrites existing state", () => {
                givenExistingBoardStateWithSize5();
                thenBoardSizeIs(5);
                givenApiStateWithSize3();

                whenSetBoardFromApi();

                thenBoardSizeIs(3);
                expect(boardStore.boardLayout[0][0]).toEqual(0);
                expect(boardStore.cardsById).not.toHaveProperty("100");
                expect(boardStore.cardsById).toHaveProperty("1");
                expect(boardStore.cardsById["8"].playerIds).toEqual([]);
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

                expect(boardStore.disabledShiftLocation).toEqual(loc(1, 2));
            });
        });

        describe("rotateLeftoverClockwise", () => {
            it("rotates leftover", () => {
                givenStoreFromApi();

                whenRotateLeftover();
                expect(boardStore.leftoverMazeCard.rotation).toEqual(90);
                whenRotateLeftover();
                expect(boardStore.leftoverMazeCard.rotation).toEqual(180);
                whenRotateLeftover();
                expect(boardStore.leftoverMazeCard.rotation).toEqual(270);
                whenRotateLeftover();
                expect(boardStore.leftoverMazeCard.rotation).toEqual(0);
            });
        });
    });

    describe("getters", () => {
        beforeEach(() => {
            setActivePinia(createPinia());
            boardStore = useBoardStore();
        });

        describe("mazeCard", () => {
            it("returns the card for a given location", () => {
                givenStoreFromApi();

                const card = whenGetMazeCard({ column: 1, row: 1 });

                expect(card).toEqual(
                    expect.objectContaining({
                        location: { column: 1, row: 1 },
                    }),
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
                for (const [id, card] of Object.entries(boardStore.cardsById)) {
                    if (parseInt(id) !== boardStore.leftoverId) {
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

let boardStore;
let apiState;

const givenExistingBoardStateWithSize5 = function () {
    let board = stateFactory();
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
    boardStore.$patch(cloneDeep(board));
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
    boardStore.update(apiState);
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
    boardStore.update(apiState);
};

const whenMove = function (moveObject) {
    boardStore.movePlayer(moveObject);
};

const whenShift = function (location, rotation) {
    boardStore.shift({ location: location, leftoverRotation: rotation });
};

const whenGetMazeCard = function (location) {
    return getMazeCard(location);
};

const whenRotateLeftover = function () {
    boardStore.rotateLeftoverClockwise();
};

const whenGetMazeCardsRowMajorOrder = function () {
    return boardStore.mazeCardsRowMajorOrder;
};

const thenBoardSizeIs = function (size) {
    expect(boardStore.mazeSize).toEqual(size);
    expect(boardStore.boardLayout.length).toEqual(size);
    for (let row = 0; row < size; row++) {
        expect(boardStore.boardLayout[row].length).toEqual(size);
    }
};

const getMazeCard = function (location) {
    return boardStore.mazeCard(location);
};

const playersOnCard = function (id) {
    return boardStore.mazeCardById(id).playerIds;
};

function loc(row, column) {
    return { row: row, column: column };
}

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
