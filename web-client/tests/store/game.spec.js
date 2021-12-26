import gameConfig from "@/store/modules/game.js";
import boardConfig from "@/store/modules/board.js";
import playersConfig from "@/store/modules/players.js";
import { SHIFT_ACTION } from "@/model/player.js";
import { createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";
import { cloneDeep } from "lodash";
import API from "@/services/game-api.js";
import { GET_GAME_STATE_RESULT_FOR_N_3 } from "../testfixtures.js";

describe("game Vuex module", () => {
    beforeEach(() => {
        API.doMove.mockClear();
        API.doShift.mockClear();
    });

    describe("getters", () => {
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

        describe("currentPlayer", () => {
            it("returns player for next action", () => {
                givenStoreFromApi();

                const player = store.getters["game/currentPlayer"];

                expect(player.id).toEqual(17);
                expect(player.nextAction).toEqual(SHIFT_ACTION);
            });
        });
    });

    describe("mutations", () => {
        describe("update", () => {
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

            it("places cards on correct locations", () => {
                givenApiStateWithSize3();

                whenGameUpdate();

                thenCardLocationsAreConsistent();
            });

            it("leaves nextAction falsy if there are no players", () => {
                givenApiStateWithoutPlayers();

                whenGameUpdate();

                expect(store.state.game.nextAction).toBeFalsy();
            });
        });

        describe("reset", () => {
            it("resets game state", () => {
                givenStoreFromApi();

                whenReset();

                thenGameHasInitialState();
            });

            it("resets board state", () => {
                givenStoreFromApi();

                whenReset();

                thenBoardIsEmpty();
            });

            it("resets player state", () => {
                givenStoreFromApi();

                whenReset();

                thenPlayersAreEmpty();
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
    apiState = cloneDeep(GET_GAME_STATE_RESULT_FOR_N_3);
};

const givenApiStateWithoutPlayers = function() {
    givenApiStateWithSize3();
    apiState.players = [];
    apiState.nextAction = null;
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

const whenReset = function() {
    store.dispatch("game/reset");
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

const thenGameHasInitialState = function() {
    expect(store.state.game).toEqual(state());
};

const thenPlayersAreEmpty = function() {
    expect(store.state.players.byId).toEqual({});
    expect(store.state.players.allIds).toEqual([]);
};

const thenBoardIsEmpty = function() {
    expect(store.state.board.boardLayout).toEqual([]);
    expect(store.state.board.mazeSize).toEqual(0);
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

function loc(row, column) {
    return { row: row, column: column };
}

API.doMove = jest.fn();
API.doShift = jest.fn();
