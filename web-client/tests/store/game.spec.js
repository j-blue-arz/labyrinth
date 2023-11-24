import { MOVE_ACTION, PREPARE_MOVE, PREPARE_SHIFT, SHIFT_ACTION } from "@/model/player.js";
import API from "@/services/game-api.js";
import { useBoardStore } from "@/stores/board.js";
import { useGameStore } from "@/stores/game.js";
import { usePlayersStore } from "@/stores/players.js";
import { cloneDeep } from "lodash";
import { createPinia, setActivePinia } from "pinia";
import { GET_GAME_STATE_RESULT_FOR_N_3 } from "../testfixtures.js";

describe("Game Store", () => {
    beforeEach(() => {
        setActivePinia(createPinia());
        stores = {
            game: useGameStore(),
            board: useBoardStore(),
            players: usePlayersStore(),
        };
        gameStore = stores.game;
        API.doMove.mockClear();
        API.doShift.mockClear();
        vi.resetModules();
    });

    describe("getters", () => {
        describe("currentPlayer", () => {
            it("returns player for next action", () => {
                givenStoreFromApi();

                thenNextActionIs(SHIFT_ACTION);
                thenNextPlayerIs(17);
            });
        });
    });

    describe("updates", () => {
        it("sets objective flag for maze card id 8", () => {
            givenApiStateWithSize3();

            whenUpdateObjective();

            expect(gameStore.objectiveId).toBe(8);
        });

        it("sets next action from api", () => {
            givenApiStateWithSize3();

            whenUpdateNextAction();

            expect(gameStore.nextAction).toEqual(apiState.nextAction);
        });
    });

    describe("actions", () => {
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

                expect(gameStore.nextAction).toBeFalsy();
            });
        });

        describe("playOffline", () => {
            it("leaves online game", () => {
                givenStoreFromApiWithUserPlayer(42);

                whenPlayOffline();

                thenPlayerIsRemovedByApi(42);
            });

            it("builds a board generated from the api", () => {
                whenPlayOffline();

                thenCardLocationsAreConsistent();
                thenBoardIsGeneratedWithSize(7);
            });

            it("chooses an objective", () => {
                whenPlayOffline();

                thenObjectiveIsAMazeCardOnTheBoard();
            });

            it("adds user player and sets piece on board", () => {
                whenPlayOffline();

                thenSinglePlayer({
                    id: 0,
                    isUser: true,
                    pieceIndex: 0,
                });
                expect(playersOnCard(loc(0, 0))).toContain(0);
            });

            it("starts offline mode with player to shift", () => {
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
                    whenMoveIsCalled(loc(0, 2), 42);

                    expect(playersOnCard(loc(1, 2))).not.toContain(42);
                    expect(playersOnCard(loc(0, 2))).toContain(42);
                });

                it("updates card of players", () => {
                    whenMoveIsCalled(loc(0, 2), 42);

                    expect(player(42).mazeCardId).toEqual(2);
                });

                it("calls API", () => {
                    whenMoveIsCalled(loc(0, 2), 42);

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
                    whenMoveIsCalled(loc(2, 0), 0);

                    expect(API.doMove).not.toHaveBeenCalled();
                });

                it("changes player's action to 'shift'", () => {
                    whenMoveIsCalled(loc(2, 0), 0);

                    thenNextActionIs(PREPARE_SHIFT);
                    thenNextPlayerIs(0);
                });

                it("increases player's score when objective is reached", () => {
                    givenObjectiveOnMazeCard(loc(1, 0));

                    whenMoveIsCalled(loc(1, 0), 0);

                    thenScoreIs(player(0), 1);
                });

                it("generates new objective when objective is reached", () => {
                    givenObjectiveOnMazeCard(loc(1, 0));

                    whenMoveIsCalled(loc(1, 0), 0);

                    thenObjectiveIsNotAt(loc(1, 0));
                });
            });
        });

        describe("shift", () => {
            it("places maze cards correctly", () => {
                givenStoreFromApi();

                whenShiftIsCalled(17, loc(0, 1), 90);

                thenCardLocationsAreConsistent();
                expect(cardOnLocation(loc(0, 1))).toHaveProperty("id", 9);
                expect(cardOnLocation(loc(1, 1))).toHaveProperty("id", 1);
                expect(cardOnLocation(loc(2, 1))).toHaveProperty("id", 4);
            });

            it("transfers players to pushed-in card", () => {
                givenStoreFromApi();

                whenShiftIsCalled(17, loc(1, 0), 90);

                expect(leftoverMazeCard().playerIds).toHaveLength(0);
                expect(playersOnCard(loc(1, 0))).toContain(42);
                expect(playersOnCard(loc(1, 0))).toContain(17);
            });

            it("updates player's maze card correctly", () => {
                givenStoreFromApi();

                whenShiftIsCalled(17, loc(1, 0), 90);

                expect(player(42).mazeCardId).toEqual(9);
                expect(player(17).mazeCardId).toEqual(9);
            });

            it("calls API", () => {
                givenStoreFromApi();

                whenShiftIsCalled(17, loc(1, 0), 90);

                expect(API.doShift).toHaveBeenCalledTimes(1);
                expect(API.doShift).toHaveBeenCalledWith(17, loc(1, 0), 90, expect.anything());
            });

            it("does not call API when playing offline", () => {
                givenPlayingOffline();

                whenShiftIsCalled(0, loc(1, 0), 90);

                expect(API.doShift).not.toHaveBeenCalled();
            });

            it("changes player's next action to 'move' when playing offline", () => {
                givenPlayingOffline();

                whenShiftIsCalled(0, loc(1, 0), 90);

                thenNextActionIs(PREPARE_MOVE);
                thenNextPlayerIs(0);
            });
        });
    });
});

let stores;
let gameStore;
let apiState;

const givenApiStateWithSize3 = function () {
    apiState = cloneDeep(GET_GAME_STATE_RESULT_FOR_N_3);
};

const givenApiStateWithoutPlayers = function () {
    givenApiStateWithSize3();
    apiState.players = [];
    apiState.nextAction = null;
};

const givenStoreFromApi = function () {
    givenApiStateWithSize3();
    givenPlayingOnline();
    updateGame();
};

const givenStoreFromApiWithUserPlayer = function (playerId) {
    givenPlayingOnline();
    stores.players.addPlayer({ id: playerId, isUser: true });
    givenApiStateWithSize3();
    updateGame();
};

const givenPlayingOnline = function () {
    gameStore.playOnline();
};

const givenPlayingOffline = function () {
    vi.doMock("@/model/board-factory.js", () => ({
        default: () => {
            let state = cloneDeep(GET_GAME_STATE_RESULT_FOR_N_3);
            return state.maze;
        },
    }));

    gameStore.playOffline();
};

const givenNextActionIs = function (playerId, nextAction) {
    gameStore.updateNextAction({ playerId: playerId, action: nextAction });
};

const givenObjectiveOnMazeCard = function (location) {
    const objectiveId = stores.board.mazeCard(location).id;
    gameStore.updateObjective(objectiveId);
};

const whenUpdateObjective = function () {
    gameStore.updateObjective(apiState.objectiveMazeCardId);
};

const whenUpdateNextAction = function () {
    gameStore.updateNextAction(apiState.nextAction);
};

const whenMoveIsCalled = function (targetLocation, playerId) {
    gameStore.move({
        targetLocation: targetLocation,
        playerId: playerId,
    });
};

const whenShiftIsCalled = function (playerId, shiftLocation, leftoverRotation) {
    const shiftAction = {
        playerId: playerId,
        location: shiftLocation,
        leftoverRotation: leftoverRotation,
    };
    gameStore.shift(shiftAction);
};

const whenGameUpdate = function () {
    updateGame();
};

const whenPlayOffline = function () {
    gameStore.playOffline();
};

const updateGame = function () {
    gameStore.updateFromApi(apiState);
};

const thenCardLocationsAreConsistent = function () {
    const n = stores.board.mazeSize;
    for (let row = 0; row < n; row++) {
        for (let col = 0; col < n; col++) {
            expect(cardOnLocation(loc(row, col)).location).toEqual(loc(row, col));
        }
    }
    expect(leftoverMazeCard().location).toBeNull();
};

const thenScoreIs = function (player, expectedScore) {
    expect(player.score).toEqual(expectedScore);
};

const thenBoardIsGeneratedWithSize = function (size) {
    const n = stores.board.mazeSize;
    expect(n).toEqual(size);
};

const thenObjectiveIsAMazeCardOnTheBoard = function () {
    const objectiveId = gameStore.objectiveId;
    expect(objectiveId).toBeGreaterThanOrEqual(0);
    const objectiveCard = stores.board.mazeCardById(gameStore.objectiveId);
    expect(objectiveCard).toBeDefined();
};

const thenObjectiveIsNotAt = function (location) {
    const prohibited = stores.board.mazeCard(location).id;
    const actual = gameStore.objectiveId;
    expect(actual).not.toEqual(prohibited);
};

const thenPlayerIsRemovedByApi = function (playerId) {
    expect(API.removePlayer).toHaveBeenCalledWith(playerId);
};

const thenSinglePlayer = function (expectedPlayer) {
    expect(stores.players.all.length === 1);
    const actualPlayer = stores.players.all[0];
    expect(actualPlayer).toEqual(expect.objectContaining(expectedPlayer));
};

const playersOnCard = function (location) {
    return stores.board.mazeCard(location).playerIds;
};

const cardOnLocation = function (location) {
    return stores.board.mazeCard(location);
};

const leftoverMazeCard = function () {
    return stores.board.leftoverMazeCard;
};

const player = function (id) {
    return stores.players.find(id);
};

function thenNextActionIs(expectedAction) {
    const player = gameStore.currentPlayer;
    expect(player.nextAction).toEqual(expectedAction);
}

function thenNextPlayerIs(expectedPlayerId) {
    const player = gameStore.currentPlayer;
    expect(player.id).toEqual(expectedPlayerId);
}

function loc(row, column) {
    return { row: row, column: column };
}

API.doMove = vi.fn();
API.doShift = vi.fn();
API.removePlayer = vi.fn();
API.fetchComputationMethods = vi.fn();
API.doAddPlayer = vi.fn();
