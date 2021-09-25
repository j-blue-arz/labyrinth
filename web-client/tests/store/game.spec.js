import gameConfig from "@/store/modules/game.js";
import boardConfig from "@/store/modules/board.js";
import playersConfig from "@/store/modules/players.js";
import { createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";
import { cloneDeep } from "lodash";
import API from "@/services/game-api.js";

describe("game Vuex module", () => {
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

        describe("move", () => {
            it("moves player to correct location", async () => {
                givenAPIreturnsStateWithSize3();

                await store.dispatch("game/updateFromApi");

                store.dispatch("game/move", {
                    targetLocation: { row: 1, column: 2 },
                    playerId: 42
                });

                expect(playersOnCard(2)).not.toContain(42);
                expect(playersOnCard(5)).toContain(42);
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

const whenCreateFromApi = function() {
    update(game, apiState);
};

const givenAPIreturnsStateWithSize3 = function() {
    jest.mock("@/services/game-api.js", () => jest.fn());
    let mockFetchState = jest.fn();
    apiState = JSON.parse(GET_STATE_RESULT_FOR_N_3);
    mockFetchState.mockImplementation(() => Promise.resolve({ data: apiState }));
    API.fetchState = mockFetchState;
};

const playersOnCard = function(cardId) {
    return store.getters["board/find"](cardId).playerIds;
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
      "players": [{
        "id": 42,
        "mazeCardId": 2,
        "pieceIndex": 0
      },{
        "id": 17,
        "pieceIndex": 1,
        "mazeCardId": 2
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
