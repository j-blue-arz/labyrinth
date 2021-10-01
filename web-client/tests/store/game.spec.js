import gameConfig from "@/store/modules/game.js";
import boardConfig from "@/store/modules/board.js";
import playersConfig from "@/store/modules/players.js";
import { createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";
import { cloneDeep } from "lodash";
import API from "@/services/game-api.js";
import { loc } from "../testutils.js";

describe("game Vuex module", () => {
    beforeEach(() => {
        API.doMove.mockClear();
        API.doShift.mockClear();
    });

    describe("mutations", () => {
        describe("update", () => {
            it("results in a game with two players", () => {
                givenInitialGameState();
                givenApiStateWithSize3();

                whenCreateFromApi();

                expect(game.playerIds).toContain(42);
                expect(game.playerIds).toContain(17);
            });

            it("sets objective flag for maze card id 8", () => {
                givenInitialGameState();
                givenApiStateWithSize3();

                whenCreateFromApi();

                expect(game.objectiveId).toBe(8);
            });

            it("sets next action from api", () => {
                givenInitialGameState();
                givenApiStateWithSize3();

                whenCreateFromApi();

                expect(game.nextAction).toBe(apiState.nextAction);
            });

            it("marks game as served by backend", () => {
                givenInitialGameState();
                givenApiStateWithSize3();

                whenCreateFromApi();

                expect(game.isServed).toBe(true);
            });
        });
    });

    describe("actions", () => {
        // actions run against real store, because they call other modules mutations and getters.
        beforeEach(() => {
            const localVue = createLocalVue();
            localVue.use(Vuex);
            store = new Vuex.Store({
                modules: {
                    game: cloneDeep(gameConfig),
                    board: cloneDeep(boardConfig),
                    players: cloneDeep(playersConfig)
                }
            });
        });

        describe("update", () => {
            it("places players on card ids", () => {
                givenApiStateWithSize3();

                whenGameUpdate();

                expect(playersOnCard(loc(1, 2))).toContain(42);
                expect(playersOnCard(loc(1, 2))).toContain(17);
            });
        });

        describe("update", () => {
            it("places cards on correct locations", () => {
                givenApiStateWithSize3();

                whenGameUpdate();

                thenCardLocationsAreConsistent();
            });
        });

        describe("move", () => {
            it("updates players on maze cards", () => {
                givenStoreFromApi();

                whenDispatchMove(loc(0, 2), 42);

                expect(playersOnCard(loc(1, 2))).not.toContain(42);
                expect(playersOnCard(loc(0, 2))).toContain(42);
            });

            it("updates card of players", () => {
                givenStoreFromApi();

                whenDispatchMove(loc(0, 2), 42);

                expect(player(42).mazeCard).toEqual(2);
            });

            it("calls API", () => {
                givenStoreFromApi();

                whenDispatchMove(loc(0, 2), 42);

                expect(API.doMove).toHaveBeenCalledTimes(1);
                expect(API.doMove).toHaveBeenCalledWith(42, loc(0, 2));
            });
        });

        describe("shift", () => {
            it("places maze cards correctly", () => {
                givenStoreFromApi();

                whenDispatchShift(17, loc(0, 1), 90);

                thenCardLocationsAreConsistent();
                expect(cardOnLocation(loc(0, 1))).toHaveProperty("id", 9);
                expect(cardOnLocation(loc(1, 1))).toHaveProperty("id", 1);
                expect(cardOnLocation(loc(2, 1))).toHaveProperty("id", 4);
            });

            it("transfers players to pushed-in card", () => {
                givenStoreFromApi();

                whenDispatchShift(17, loc(1, 0), 90);

                expect(leftoverMazeCard().playerIds).toHaveLength(0);
                expect(playersOnCard(loc(1, 0))).toContain(42);
                expect(playersOnCard(loc(1, 0))).toContain(17);
            });

            it("updates player's maze card correctly", () => {
                givenStoreFromApi();

                whenDispatchShift(17, loc(1, 0), 90);

                expect(player(42).mazeCard).toEqual(9);
                expect(player(17).mazeCard).toEqual(9);
            });

            it("calls API", () => {
                givenStoreFromApi();

                whenDispatchShift(17, loc(1, 0), 90);

                expect(API.doShift).toHaveBeenCalledTimes(1);
                expect(API.doShift).toHaveBeenCalledWith(17, loc(1, 0), 90, expect.anything());
            });
        });
    });
});

const { state, mutations } = gameConfig;
const { update } = mutations;

let store;
let game;
let apiState;

const givenInitialGameState = function() {
    game = state();
};

const givenApiStateWithSize3 = function() {
    apiState = JSON.parse(GET_STATE_RESULT_FOR_N_3);
};

const givenStoreFromApi = function() {
    givenApiStateWithSize3();
    updateGame();
};

const whenCreateFromApi = function() {
    update(game, apiState);
};

const whenDispatchMove = function(targetLocation, playerId) {
    store.dispatch("game/move", {
        targetLocation: targetLocation,
        playerId: playerId
    });
};

const whenDispatchShift = function(playerId, shiftLocation, leftoverRotation) {
    const shiftAction = {
        playerId: playerId,
        location: shiftLocation,
        leftoverRotation: leftoverRotation
    };
    store.dispatch("game/shift", shiftAction);
};

const whenGameUpdate = function() {
    updateGame();
};

const updateGame = function() {
    store.dispatch("game/update", apiState);
};

const thenCardLocationsAreConsistent = function() {
    const n = store.state.board.mazeSize;
    for (let row = 0; row < n; row++) {
        for (let col = 0; col < n; col++) {
            expect(cardOnLocation(loc(row, col)).location).toEqual(loc(row, col));
        }
    }
    expect(leftoverMazeCard().location).toBeNull();
};

const playersOnCard = function(location) {
    return store.getters["board/mazeCard"](location).playerIds;
};

const cardOnLocation = function(location) {
    return store.getters["board/mazeCard"](location);
};

const leftoverMazeCard = function() {
    return store.getters["board/leftoverMazeCard"];
};

const player = function(id) {
    return store.getters["players/find"](id);
};

API.doMove = jest.fn();
API.doShift = jest.fn();

const GET_STATE_RESULT_FOR_N_3 = `{
    "maze": {
        "mazeSize": 3,
        "mazeCards": [{
            "outPaths": "NES",
            "id": 9,
            "location": null,
            "rotation": 90
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
      "players": [{
        "id": 42,
        "mazeCardId": 5,
        "pieceIndex": 0
      },{
        "id": 17,
        "pieceIndex": 1,
        "mazeCardId": 5
      }],
    "objectiveMazeCardId": 8,
    "enabledShiftLocations": [
      {"column": 1, "row": 0},
      {"column": 0, "row": 1},
      {"column": 2, "row": 1}
    ],
    "nextAction": {
      "action": "SHIFT",
      "playerId": 17
    }
  }`;
