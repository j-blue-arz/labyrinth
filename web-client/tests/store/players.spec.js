import { NO_ACTION, SHIFT_ACTION } from "@/model/player.js";
import API from "@/services/game-api.js";
import { useBoardStore } from "@/stores/board.js";
import { useGameStore } from "@/stores/game.js";
import { usePlayersStore } from "@/stores/players.js";
import { cloneDeep } from "lodash";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { GET_GAME_STATE_RESULT_FOR_N_3 } from "../testfixtures.js";

describe("Players Store", () => {
    beforeEach(() => {
        setActivePinia(createPinia());
        stores = {
            game: useGameStore(),
            board: useBoardStore(),
            players: usePlayersStore(),
        };
        playersStore = stores.players;
        API.doAddPlayer.mockClear();
        API.removePlayer.mockClear();
        API.changePlayerName.mockClear();
        givenPlayingOnline();
    });

    describe("getters", () => {
        describe("find", () => {
            it("returns player with next action if next action is present", () => {
                const nextAction = { action: SHIFT_ACTION, playerId: 2 };
                givenPlayerInState({ id: 2, isUser: true, pieceIndex: 1 });
                givenNextAction(nextAction);

                const player = findPlayer(2);

                expect(player.nextAction).toEqual(SHIFT_ACTION);
            });

            it("returns player with next action equals to no action, if next action is not present in game", () => {
                givenPlayerInState({ id: 2, isUser: true, pieceIndex: 1 });

                const player = findPlayer(2);

                expect(player.nextAction).toEqual(NO_ACTION);
            });
        });

        describe("bots", () => {
            it("returns only bots of current list of players", () => {
                givenPlayersInState([
                    { id: 2, isUser: true, pieceIndex: 1 },
                    { id: 3, isBot: true, pieceIndex: 2 },
                    { id: 4, isBot: true, pieceIndex: 3 },
                ]);

                const bots = playersStore.bots;

                expect(bots).toEqual(
                    expect.arrayContaining([
                        expect.objectContaining({ id: 3, isBot: true, pieceIndex: 2 }),
                        expect.objectContaining({ id: 4, isBot: true, pieceIndex: 3 }),
                    ]),
                );
            });
        });

        describe("userPlayer", () => {
            it("returns undefined if user is not playing", () => {
                givenPlayersInState([
                    { id: 3, isBot: true, pieceIndex: 2 },
                    { id: 4, isBot: true, pieceIndex: 3 },
                ]);

                const userPlayer = playersStore.userPlayer;

                expect(userPlayer).toBeUndefined();
            });
        });
    });

    describe("actions", () => {
        describe("enterGame", () => {
            it("does not call API if user is already playing", () => {
                givenPlayerInState({ id: 2, isUser: true });

                whenEnterGame();

                expect(API.doAddPlayer).not.toHaveBeenCalled();
            });

            it("calls API", () => {
                givenNoPlayersInState();

                whenEnterGame();

                expect(API.doAddPlayer).toHaveBeenCalledTimes(1);
            });

            it("adds user to players with id from API", () => {
                givenNoPlayersInState();
                givenApiAddPlayerReturns({
                    id: 42,
                    mazeCardId: 5,
                    pieceIndex: 0,
                });

                whenEnterGame();

                expect(playersStore.find(42).isUser).toBe(true);
                expect(playersStore.hasUserPlayer).toBe(true);
            });

            it("adds player to maze card", () => {
                givenPlayingOffline();
                whenLeaveGame();

                whenEnterGame();

                const userPlayer = playersStore.userPlayer;
                const playerMazeCard = stores.board.mazeCardById(userPlayer.mazeCardId);
                expect(playerMazeCard.playerIds).toEqual([userPlayer.id]);
            });
        });

        describe("leaveGame", () => {
            it("does not call API if no user is not playing", () => {
                givenNoPlayersInState();

                whenLeaveGame();

                expect(API.removePlayer).not.toHaveBeenCalled();
            });

            it("calls API", () => {
                const userPlayerId = 2;
                givenPlayerInState({ id: userPlayerId, isUser: true });

                whenLeaveGame();

                expect(API.removePlayer).toHaveBeenCalledTimes(1);
                expect(API.removePlayer).toHaveBeenCalledWith(userPlayerId);
            });

            it("removes user from players", () => {
                givenPlayerInState({ id: 2, isUser: true });

                whenLeaveGame();

                expect(playersStore.hasUserPlayer).toBe(false);
            });
        });

        describe("addWasmPlayer", () => {
            it("does not call API if WASM player is already playing", () => {
                givenPlayerInState({ id: 2, isWasm: true });

                whenAddWasmPlayer();

                expect(API.doAddPlayer).not.toHaveBeenCalled();
            });

            it("calls API", () => {
                givenNoPlayersInState();

                whenAddWasmPlayer();

                expect(API.doAddPlayer).toHaveBeenCalledTimes(1);
            });

            it("adds WASM to players with id from API", () => {
                givenNoPlayersInState();
                givenApiAddPlayerReturns({
                    id: 42,
                    mazeCardId: 5,
                    pieceIndex: 0,
                });

                whenAddWasmPlayer();

                expect(findPlayer(42).isUser).toBeFalsy;
                expect(playersStore.hasUserPlayer).toBe(false);
                expect(findPlayer(42).isWasm).toBe(true);
                expect(playersStore.hasWasmPlayer).toBe(true);
            });
        });

        describe("removeWasmPlayer", () => {
            it("does not call API if WASM player is not playing", () => {
                givenNoPlayersInState();

                whenRemoveWasmPlayer();

                expect(API.removePlayer).not.toHaveBeenCalled();
            });

            it("calls API", () => {
                const wasmPlayerId = 2;
                givenPlayerInState({ id: wasmPlayerId, isWasm: true });

                whenRemoveWasmPlayer();

                expect(API.removePlayer).toHaveBeenCalledTimes(1);
                expect(API.removePlayer).toHaveBeenCalledWith(wasmPlayerId);
            });

            it("removes WASM player from players", () => {
                givenPlayerInState({ id: 2, isWasm: true });

                whenRemoveWasmPlayer();

                expect(playersStore.hasWasmPlayer).toBe(false);
            });
        });

        describe("removeAllClientPlayers", () => {
            it("removes only client players from state", () => {
                givenPlayersInState([
                    { id: 2, isWasm: true, mazeCardId: 2 },
                    { id: 5, isUser: true, mazeCardId: 4 },
                    { id: 7, isWasm: false, isUser: false, mazeCardId: 3 },
                ]);

                whenRemoveAllClientPlayers();

                expect(playersStore.hasWasmPlayer).toBe(false);
                expect(playersStore.hasUserPlayer).toBe(false);
                expect(findPlayer(2)).toBeFalsy();
                expect(findPlayer(5)).toBeFalsy();
                expect(findPlayer(7)).toBeTruthy();
            });

            it("removes calls API with players to remove", () => {
                givenPlayersInState([
                    { id: 2, isWasm: true, mazeCardId: 2 },
                    { id: 5, isUser: true, mazeCardId: 4 },
                    { id: 7, isWasm: false, isUser: false, mazeCardId: 3 },
                ]);

                whenRemoveAllClientPlayers();

                expect(API.removePlayer).toHaveBeenCalledTimes(2);
                expect(API.removePlayer).toHaveBeenCalledWith(2);
                expect(API.removePlayer).toHaveBeenCalledWith(5);
            });
        });

        describe("removeClientPlayer", () => {
            it("does not remove player if not managed by client", () => {
                givenPlayerInState({ id: 7, isWasm: false, isUser: false, mazeCardId: 2 });

                whenRemoveClientPlayer(7);

                expect(findPlayer(7)).toBeTruthy();
                expect(API.removePlayer).not.toHaveBeenCalled();
            });

            it("removes player if managed by client", () => {
                givenPlayersInState([
                    { id: 2, isWasm: true, mazeCardId: 2 },
                    { id: 5, isUser: true, mazeCardId: 4 },
                    { id: 7, isWasm: false, isUser: false, mazeCardId: 3 },
                ]);

                whenRemoveClientPlayer(5);

                expect(findPlayer(5)).toBeFalsy();
                expect(API.removePlayer).toHaveBeenCalledTimes(1);
                expect(API.removePlayer).toHaveBeenCalledWith(5);
            });

            it("removes player from maze card", () => {
                givenPlayingOffline();

                whenLeaveGame();

                const mazeCards = stores.board.allIds.map((id) => stores.board.mazeCardById(id));

                mazeCards.forEach((mazeCard) => {
                    expect(mazeCard.playerIds.length).toEqual(0);
                });
            });
        });

        describe("changeUserPlayerName", () => {
            it("does not call API if user is not playing", () => {
                givenPlayerInState({ id: 7, isWasm: false, isUser: false, name: "felix" });

                whenChangeUserPlayerName("gina");

                expect(API.changePlayerName).not.toHaveBeenCalled();
                expect(playersStore.byId[7].name).toBe("felix");
            });

            it("changes name if user is playing", () => {
                givenPlayerInState({ id: 7, isWasm: false, isUser: true, name: "felix" });

                whenChangeUserPlayerName("gina");

                expect(playersStore.byId[7].name).toBe("gina");
            });

            it("calls API if user is playing", () => {
                givenPlayerInState({ id: 7, isWasm: false, isUser: true, name: "felix" });

                whenChangeUserPlayerName("gina");

                expect(API.changePlayerName).toHaveBeenCalledTimes(1);
                expect(API.changePlayerName).toHaveBeenCalledWith(7, "gina");
            });
        });

        describe("update", () => {
            beforeEach(() => {
                apiPlayers = [];
                givenApiPlayer({
                    id: 42,
                    mazeCardId: 16,
                    pieceIndex: 0,
                    isBot: true,
                    computationMethod: "random",
                });
                givenApiPlayer({
                    id: 17,
                    pieceIndex: 1,
                    mazeCardId: 15,
                    score: 12,
                    name: "Fred",
                });
            });

            it("sets correct number of players for empty game", () => {
                givenNoPlayersInState();

                whenSetPlayersFromApi();

                thenPlayerExists(42);
                thenPlayerExists(17);
            });

            it("fills bot from api", () => {
                givenNoPlayersInState();

                whenSetPlayersFromApi();

                const botPlayer = findPlayer(42);
                expect(botPlayer.id).toBe(42);
                expect(botPlayer.mazeCardId).toBe(16);
                expect(botPlayer.pieceIndex).toBe(0);
                expect(botPlayer.score).toBe(0);
                expect(botPlayer.isBot).toBe(true);
                expect(botPlayer.computationMethod).toBe("random");
                expect(botPlayer.name).toBe("");
            });

            it("fills human player from api", () => {
                givenNoPlayersInState();

                whenSetPlayersFromApi();

                const player = findPlayer(17);
                expect(player.id).toBe(17);
                expect(player.mazeCardId).toBe(15);
                expect(player.pieceIndex).toBe(1);
                expect(player.score).toBe(12);
                expect(player.isBot).toBeFalsy();
                expect(player.name).toBe("Fred");
            });

            it("keeps value of isUser for existing user player", () => {
                givenPlayerInState({ id: 2, isUser: true });
                givenApiPlayer({
                    id: 2,
                    pieceIndex: 1,
                    mazeCardId: 15,
                });

                whenSetPlayersFromApi();

                expect(findPlayer(2).isUser).toBe(true);
            });

            it("keeps value of isUser for existing non-user player", () => {
                givenPlayerInState({ id: 2, isUser: false });
                givenApiPlayer({
                    id: 2,
                    pieceIndex: 1,
                    mazeCardId: 15,
                });

                whenSetPlayersFromApi();

                expect(findPlayer(2).isUser).toBeFalsy();
            });

            it("sets isUser to false for new players", () => {
                givenNoPlayersInState();

                whenSetPlayersFromApi();

                expect(findPlayer(17).isUser).toBeFalsy();
            });

            it("removes player if not present in api", () => {
                givenPlayerInState({ id: 2 });

                whenSetPlayersFromApi();

                thenPlayerDoesNotExist(2);
            });
        });
    });
});

API.doAddPlayer = vi.fn();
API.removePlayer = vi.fn();
API.changePlayerName = vi.fn();

let stores;
let playersStore;
let apiPlayers = [];

const givenPlayingOnline = function () {
    let apiState = cloneDeep(GET_GAME_STATE_RESULT_FOR_N_3);
    apiState.players = [];
    apiState.nextAction = {};
    stores.game.online();
    stores.game.updateFromApi(apiState);
};

const givenPlayingOffline = function () {
    vi.doMock("@/model/board-factory.js", () => ({
        default: () => {
            return cloneDeep(GET_GAME_STATE_RESULT_FOR_N_3).state;
        },
    }));

    stores.game.playOffline();
};

const givenNoPlayersInState = function () {
    playersStore.$reset();
};

const givenPlayerInState = function (player) {
    const playerId = player.id;
    playersStore.$patch({ byId: { [playerId]: player }, allIds: [playerId] });
};

const givenPlayersInState = function (players) {
    const byId = players.reduce((result, player) => {
        result[player.id] = player;
        return result;
    }, {});
    playersStore.$patch({ byId: byId, allIds: players.map((player) => player.id) });
};

const givenNextAction = function (nextAction) {
    stores.game.updateNextAction(nextAction);
};

const givenApiPlayer = function (apiPlayer) {
    apiPlayers.push(apiPlayer);
};

const givenApiAddPlayerReturns = function (apiPlayer) {
    API.doAddPlayer.mockImplementation((cb) => cb(apiPlayer));
};

const whenSetPlayersFromApi = function () {
    playersStore.update(apiPlayers);
};

const whenEnterGame = function () {
    playersStore.enterGame();
};

const whenLeaveGame = function () {
    playersStore.leaveGame();
};

const whenAddWasmPlayer = function () {
    playersStore.addWasmPlayer();
};

const whenRemoveWasmPlayer = function () {
    playersStore.removeWasmPlayer();
};

const whenRemoveAllClientPlayers = function () {
    playersStore.removeAllClientPlayers();
};

const whenRemoveClientPlayer = function (id) {
    playersStore.removeClientPlayer(id);
};

const whenChangeUserPlayerName = function (newName) {
    playersStore.changeUserPlayerName(newName);
};

const thenPlayerExists = function (id) {
    const state = playersStore.$state;
    expect(state.byId).toHaveProperty("" + id);
    expect(state.allIds).toContain(id);
};

const thenPlayerDoesNotExist = function (id) {
    const state = playersStore.$state;
    expect(state.byId).not.toHaveProperty("" + id);
    expect(state.allIds).not.toContain(id);
};

const findPlayer = function (id) {
    return playersStore.find(id);
};
