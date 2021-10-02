import playerConfig from "@/store/modules/players.js";
import { createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";
import { cloneDeep } from "lodash";
import API from "@/services/game-api.js";

describe("players Vuex module", () => {
    beforeEach(() => {
        const localVue = createLocalVue();
        localVue.use(Vuex);
        store = new Vuex.Store(cloneDeep(playerConfig));
        API.doAddPlayer.mockClear();
        API.removePlayer.mockClear();
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
                    pieceIndex: 0
                });

                whenEnterGame();

                expect(store.getters.find(42).isUser).toBe(true);
                expect(store.getters.hasUserPlayer).toBe(true);
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
                expect(store.getters.hasUserPlayer).toBe(true);

                whenLeaveGame();

                expect(store.getters.hasUserPlayer).toBe(false);
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

                expect(store.getters.hasUserPlayer).toBe(false);
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
                    pieceIndex: 0
                });

                whenAddWasmPlayer();

                expect(store.getters.find(42).isUser).toBeFalsy;
                expect(store.getters.hasUserPlayer).toBe(false);
                expect(store.getters.find(42).isWasm).toBe(true);
                expect(store.getters.hasWasmPlayer).toBe(true);
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

                expect(store.getters.hasWasmPlayer).toBe(false);
            });
        });

        describe("removeAllClientPlayers", () => {
            it("removes only client players from state", () => {
                givenPlayersInState([
                    { id: 2, isWasm: true },
                    { id: 5, isUser: true },
                    { id: 7, isWasm: false, isUser: false }
                ]);

                whenRemoveAllClientPlayers();

                expect(store.getters.hasWasmPlayer).toBe(false);
                expect(store.getters.hasUserPlayer).toBe(false);
                expect(store.getters.find(2)).toBeFalsy();
                expect(store.getters.find(5)).toBeFalsy();
                expect(store.getters.find(7)).toBeTruthy();
            });

            it("removes calls API with players to remove", () => {
                givenPlayersInState([
                    { id: 2, isWasm: true },
                    { id: 5, isUser: true },
                    { id: 7, isWasm: false, isUser: false }
                ]);

                whenRemoveAllClientPlayers();

                expect(API.removePlayer).toHaveBeenCalledTimes(2);
                expect(API.removePlayer).toHaveBeenCalledWith(2);
                expect(API.removePlayer).toHaveBeenCalledWith(5);
            });
        });

        describe("removeClientPlayer", () => {
            it("does not remove player if not managed by client", () => {
                givenPlayerInState({ id: 7, isWasm: false, isUser: false });

                whenRemoveClientPlayer(7);

                expect(store.getters.find(7)).toBeTruthy();
                expect(API.removePlayer).not.toHaveBeenCalled();
            });

            it("removes player if managed by client", () => {
                givenPlayersInState([
                    { id: 2, isWasm: true },
                    { id: 5, isUser: true },
                    { id: 7, isWasm: false, isUser: false }
                ]);

                whenRemoveClientPlayer(5);

                expect(store.getters.find(5)).toBeFalsy();
                expect(API.removePlayer).toHaveBeenCalledTimes(1);
                expect(API.removePlayer).toHaveBeenCalledWith(5);
            });
        });
    });

    describe("mutations", () => {
        describe("update", () => {
            beforeEach(() => {
                apiPlayers = [];
                givenApiPlayer({
                    id: 42,
                    mazeCardId: 16,
                    pieceIndex: 0,
                    isBot: true,
                    computationMethod: "random"
                });
                givenApiPlayer({
                    id: 17,
                    pieceIndex: 1,
                    mazeCardId: 15,
                    score: 12,
                    name: "Fred"
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

                const botPlayer = playerWithId(42);
                expect(botPlayer.id).toBe(42);
                expect(botPlayer.mazeCard).toBe(16);
                expect(botPlayer.pieceIndex).toBe(0);
                expect(botPlayer.isBot).toBe(true);
                expect(botPlayer.computationMethod).toBe("random");
                expect(botPlayer.name).toBe("");
            });

            it("fills human player from api", () => {
                givenNoPlayersInState();

                whenSetPlayersFromApi();

                const player = playerWithId(17);
                expect(player.id).toBe(17);
                expect(player.mazeCard).toBe(15);
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
                    mazeCardId: 15
                });

                whenSetPlayersFromApi();

                expect(playerWithId(2).isUser).toBe(true);
            });

            it("keeps value of isUser for existing non-user player", () => {
                givenPlayerInState({ id: 2, isUser: false });
                givenApiPlayer({
                    id: 2,
                    pieceIndex: 1,
                    mazeCardId: 15
                });

                whenSetPlayersFromApi();

                expect(playerWithId(2).isUser).toBeFalsy();
            });

            it("sets isUser to false for new players", () => {
                givenNoPlayersInState();

                whenSetPlayersFromApi();

                expect(playerWithId(17).isUser).toBeFalsy();
            });

            it("removes player if not present in api", () => {
                givenPlayerInState({ id: 2 });

                whenSetPlayersFromApi();

                thenPlayerDoesNotExist(2);
            });
        });
    });
});

const { state, mutations } = playerConfig;
const { update } = mutations;

API.doAddPlayer = jest.fn();
API.removePlayer = jest.fn();

let store;
let players;
let apiPlayers = [];

const givenNoPlayersInState = function() {
    players = state();
    store.replaceState(cloneDeep(players));
};

const givenPlayerInState = function(player) {
    const playerId = player.id;
    players = { byId: { [playerId]: player }, allIds: [playerId] };
    store.replaceState(cloneDeep(players));
};

const givenPlayersInState = function(players) {
    const byId = players.reduce((result, player) => {
        result[player.id] = player;
        return result;
    }, {});
    players = { byId: byId, allIds: players.map(player => player.id) };
    store.replaceState(cloneDeep(players));
};

const givenApiPlayer = function(apiPlayer) {
    apiPlayers.push(apiPlayer);
};

const givenApiAddPlayerReturns = function(apiPlayer) {
    API.doAddPlayer.mockImplementation(cb => cb(apiPlayer));
};

const whenSetPlayersFromApi = function() {
    update(players, apiPlayers);
};

const whenEnterGame = function() {
    store.dispatch("enterGame");
};

const whenLeaveGame = function() {
    store.dispatch("leaveGame");
};

const whenAddWasmPlayer = function() {
    store.dispatch("addWasmPlayer");
};

const whenRemoveWasmPlayer = function() {
    store.dispatch("removeWasmPlayer");
};

const whenRemoveAllClientPlayers = function() {
    store.dispatch("removeAllClientPlayers");
};

const whenRemoveClientPlayer = function(id) {
    store.dispatch("removeClientPlayer", id);
}

const thenPlayerExists = function(id) {
    expect(players.byId).toHaveProperty("" + id);
    expect(players.allIds).toContain(id);
};

const thenPlayerDoesNotExist = function(id) {
    expect(players.byId).not.toHaveProperty("" + id);
    expect(players.allIds).not.toContain(id);
};

const playerWithId = function(id) {
    return players.byId[id];
};
