import gameConfig from "@/store/modules/game.js";
import boardConfig from "@/store/modules/board.js";
import playersConfig from "@/store/modules/players.js";
import { SHIFT_ACTION, MOVE_ACTION, PREPARE_MOVE, PREPARE_SHIFT } from "@/model/player.js";
import { createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";
import { cloneDeep } from "lodash";
import API from "@/services/game-api.js";
import generateBoard from "@/model/board-factory.js";
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

                thenNextActionIs(SHIFT_ACTION);
                thenNextPlayerIs(17);
            });
        });
    });

    describe("mutations", () => {
        describe("updates", () => {
            it("sets objective flag for maze card id 8", () => {
                givenInitialGameState();
                givenApiStateWithSize3();

                whenUpdateObjective();

                expect(game.objectiveId).toBe(8);
            });

            it("sets next action from api", () => {
                givenInitialGameState();
                givenApiStateWithSize3();

                whenUpdateNextAction();

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

        describe("playOffline", () => {
            it("leaves online game", () => {
                givenStoreFromApiWithUserPlayer(42);

                whenPlayOffline();

                thenPlayerIsRemovedByApi(42);
            });

            it("builds a board generated from the api", () => {
                givenInitialGameState();

                whenPlayOffline();

                thenCardLocationsAreConsistent();
                thenBoardIsGeneratedWithSize(7);
            });

            it("chooses an objective", () => {
                givenInitialGameState();

                whenPlayOffline();

                thenObjectiveIsAMazeCardOnTheBoard();
            });

            it("adds user player and sets piece on board", () => {
                givenInitialGameState();

                whenPlayOffline();

                thenSinglePlayer({
                    id: 0,
                    isUser: true,
                    pieceIndex: 0
                });
                expect(playersOnCard(loc(0, 0))).toContain(0);
            });

            it("starts offline mode with player to shift", () => {
                givenInitialGameState();

                whenPlayOffline();

                thenNextActionIs(PREPARE_SHIFT);
            });
        });

        describe("move", () => {
            describe("when playing online", () => {
                beforeEach(() => {
                    givenStoreFromApi();
                });

                it("updates players on maze cards", () => {
                    whenDispatchMove(loc(0, 2), 42);

                    expect(playersOnCard(loc(1, 2))).not.toContain(42);
                    expect(playersOnCard(loc(0, 2))).toContain(42);
                });

                it("updates card of players", () => {
                    whenDispatchMove(loc(0, 2), 42);

                    expect(player(42).mazeCardId).toEqual(2);
                });

                it("calls API", () => {
                    whenDispatchMove(loc(0, 2), 42);

                    expect(API.doMove).toHaveBeenCalledTimes(1);
                    expect(API.doMove).toHaveBeenCalledWith(42, loc(0, 2));
                });
            });

            describe("when playing offline", () => {
                beforeEach(() => {
                    givenPlayingOffline();
                    givenNextActionIs(0, MOVE_ACTION);
                });

                it("does not call API", () => {
                    whenDispatchMove(loc(2, 0), 0);

                    expect(API.doMove).not.toHaveBeenCalled();
                });

                it("changes player's action to 'shift'", () => {
                    whenDispatchMove(loc(2, 0), 0);

                    thenNextActionIs(PREPARE_SHIFT);
                    thenNextPlayerIs(0);
                });

                it("increases player's score when objective is reached", () => {
                    givenObjectiveOnMazeCard(loc(1, 0));

                    whenDispatchMove(loc(1, 0), 0);

                    thenScoreIs(player(0), 1);
                });

                it("generates new objective when objective is reached", () => {
                    givenObjectiveOnMazeCard(loc(1, 0));

                    whenDispatchMove(loc(1, 0), 0);

                    thenObjectiveIsNotAt(loc(1, 0));
                });
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

                expect(player(42).mazeCardId).toEqual(9);
                expect(player(17).mazeCardId).toEqual(9);
            });

            it("calls API", () => {
                givenStoreFromApi();

                whenDispatchShift(17, loc(1, 0), 90);

                expect(API.doShift).toHaveBeenCalledTimes(1);
                expect(API.doShift).toHaveBeenCalledWith(17, loc(1, 0), 90, expect.anything());
            });

            it("does not call API when playing offline", () => {
                givenPlayingOffline();

                whenDispatchShift(0, loc(1, 0), 90);

                expect(API.doShift).not.toHaveBeenCalled();
            });

            it("changes player's next action to 'move' when playing offline", () => {
                givenPlayingOffline();

                whenDispatchShift(0, loc(1, 0), 90);

                thenNextActionIs(PREPARE_MOVE);
                thenNextPlayerIs(0);
            });
        });
    });
});

const { state, mutations } = gameConfig;
const { updateNextAction, updateObjective } = mutations;

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
    givenPlayingOnline();
    updateGame();
};

const givenStoreFromApiWithUserPlayer = function(playerId) {
    givenPlayingOnline();
    store.commit("players/addPlayer", { id: playerId, isUser: true });
    givenApiStateWithSize3();
    updateGame();
};

const givenPlayingOnline = function() {
    store.dispatch("game/playOnline");
};

const givenPlayingOffline = function() {
    function mockState() {
        let state = cloneDeep(GET_GAME_STATE_RESULT_FOR_N_3);
        return state.maze;
    }

    jest.mock("@/model/board-factory.js", () => ({
        default: size => {
            return mockState();
        }
    }));

    store.dispatch("game/playOffline");
};

const givenNextActionIs = function(playerId, nextAction) {
    store.commit("game/updateNextAction", { playerId: playerId, action: nextAction });
};

const givenObjectiveOnMazeCard = function(location) {
    const objectiveId = store.getters["board/mazeCard"](location).id;
    store.commit("game/updateObjective", objectiveId);
};

const whenUpdateObjective = function() {
    updateObjective(game, apiState.objectiveMazeCardId);
};

const whenUpdateNextAction = function() {
    updateNextAction(game, apiState.nextAction);
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

const whenPlayOffline = function() {
    store.dispatch("game/playOffline");
};

const updateGame = function() {
    store.dispatch("game/updateFromApi", apiState);
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

const thenScoreIs = function(player, expectedScore) {
    expect(player.score).toEqual(expectedScore);
};

const thenBoardIsGeneratedWithSize = function(size) {
    const n = store.state.board.mazeSize;
    expect(n).toEqual(size);
};

const thenObjectiveIsAMazeCardOnTheBoard = function() {
    const objectiveId = store.state.game.objectiveId;
    expect(objectiveId).toBeGreaterThanOrEqual(0);
    const objectiveCard = store.getters["board/mazeCardById"](store.state.game.objectiveId);
    expect(objectiveCard).toBeDefined();
};

const thenObjectiveIsNotAt = function(location) {
    const prohibited = store.getters["board/mazeCard"](location).id;
    const actual = store.state.game.objectiveId;
    expect(actual).not.toEqual(prohibited);
};

const thenPlayerIsRemovedByApi = function(playerId) {
    expect(API.removePlayer).toHaveBeenCalledWith(playerId);
};

const thenSinglePlayer = function(expectedPlayer) {
    expect(store.getters["players/all"].length === 1);
    const actualPlayer = store.getters["players/all"][0];
    expect(actualPlayer).toEqual(expect.objectContaining(expectedPlayer));
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

function thenNextActionIs(expectedAction) {
    const player = store.getters["game/currentPlayer"];
    expect(player.nextAction).toEqual(expectedAction);
}

function thenNextPlayerIs(expectedPlayerId) {
    const player = store.getters["game/currentPlayer"];
    expect(player.id).toEqual(expectedPlayerId);
}

function loc(row, column) {
    return { row: row, column: column };
}

API.doMove = jest.fn();
API.doShift = jest.fn();
API.removePlayer = jest.fn();
