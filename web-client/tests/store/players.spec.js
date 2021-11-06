import playersConfig from "@/store/modules/players.js";
import gameConfig from "@/store/modules/game.js";
import boardConfig from "@/store/modules/board.js";
import { createLocalVue } from "@vue/test-utils";
import Vuex from "vuex";
import { cloneDeep } from "lodash";
import API from "@/services/game-api.js";
import { SHIFT_ACTION, NO_ACTION } from "@/model/player.js";

describe("players Vuex module", () => {
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
        API.doAddPlayer.mockClear();
        API.removePlayer.mockClear();
        API.changePlayerName.mockClear();
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
                    { id: 4, isBot: true, pieceIndex: 3 }
                ]);

                const bots = store.getters["players/bots"];

                expect(bots).toEqual(
                    expect.arrayContaining([
                        expect.objectContaining({ id: 3, isBot: true, pieceIndex: 2 }),
                        expect.objectContaining({ id: 4, isBot: true, pieceIndex: 3 })
                    ])
                );
            });
        });

        describe("userPlayer", () => {
            it("returns undefined if user is not playing", () => {
                givenPlayersInState([
                    { id: 3, isBot: true, pieceIndex: 2 },
                    { id: 4, isBot: true, pieceIndex: 3 }
                ]);

                const userPlayer = store.getters.userPlayer;

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
                    pieceIndex: 0
                });

                whenEnterGame();

                expect(store.getters["players/find"](42).isUser).toBe(true);
                expect(store.getters["players/hasUserPlayer"]).toBe(true);
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
                expect(store.getters["players/hasUserPlayer"]).toBe(true);

                whenLeaveGame();

                expect(store.getters["players/hasUserPlayer"]).toBe(false);
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

                expect(store.getters["players/hasUserPlayer"]).toBe(false);
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

                expect(findPlayer(42).isUser).toBeFalsy;
                expect(store.getters["players/hasUserPlayer"]).toBe(false);
                expect(findPlayer(42).isWasm).toBe(true);
                expect(store.getters["players/hasWasmPlayer"]).toBe(true);
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

                expect(store.getters["players/hasWasmPlayer"]).toBe(false);
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

                expect(store.getters["players/hasWasmPlayer"]).toBe(false);
                expect(store.getters["players/hasUserPlayer"]).toBe(false);
                expect(findPlayer(2)).toBeFalsy();
                expect(findPlayer(5)).toBeFalsy();
                expect(findPlayer(7)).toBeTruthy();
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

                expect(findPlayer(7)).toBeTruthy();
                expect(API.removePlayer).not.toHaveBeenCalled();
            });

            it("removes player if managed by client", () => {
                givenPlayersInState([
                    { id: 2, isWasm: true },
                    { id: 5, isUser: true },
                    { id: 7, isWasm: false, isUser: false }
                ]);

                whenRemoveClientPlayer(5);

                expect(findPlayer(5)).toBeFalsy();
                expect(API.removePlayer).toHaveBeenCalledTimes(1);
                expect(API.removePlayer).toHaveBeenCalledWith(5);
            });
        });

        describe("changeUserPlayerName", () => {
            it("does not call API if user is not playing", () => {
                givenPlayerInState({ id: 7, isWasm: false, isUser: false, name: "felix" });

                whenChangeUserPlayerName("gina");

                expect(API.changePlayerName).not.toHaveBeenCalled();
                expect(store.state.players.byId[7].name).toBe("felix");
            });

            it("changes name if user is playing", () => {
                givenPlayerInState({ id: 7, isWasm: false, isUser: true, name: "felix" });

                whenChangeUserPlayerName("gina");

                expect(store.state.players.byId[7].name).toBe("gina");
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

                const botPlayer = findPlayer(42);
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

                const player = findPlayer(17);
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

                expect(findPlayer(2).isUser).toBe(true);
            });

            it("keeps value of isUser for existing non-user player", () => {
                givenPlayerInState({ id: 2, isUser: false });
                givenApiPlayer({
                    id: 2,
                    pieceIndex: 1,
                    mazeCardId: 15
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

const { state } = playersConfig;

API.doAddPlayer = jest.fn();
API.removePlayer = jest.fn();
API.changePlayerName = jest.fn();

let store;
let apiPlayers = [];

const givenNoPlayersInState = function() {
    let players = state();
    store.replaceState({
        game: store.state.game,
        players: players,
        board: store.state.board
    });
};

const givenPlayerInState = function(player) {
    const playerId = player.id;
    let players = { byId: { [playerId]: player }, allIds: [playerId] };
    store.replaceState({
        game: store.state.game,
        players: players,
        board: store.state.board
    });
};

const givenPlayersInState = function(players) {
    const byId = players.reduce((result, player) => {
        result[player.id] = player;
        return result;
    }, {});
    let storePlayers = { byId: byId, allIds: players.map(player => player.id) };
    store.replaceState({
        game: store.state.game,
        players: storePlayers,
        board: store.state.board
    });
};

const givenNextAction = function(nextAction) {
    const players = store.state.players;
    store.commit("game/update", {
        players: players.allIds.map(id => players.byId[id]),
        objectiveMazeCardId: 0,
        nextAction: nextAction
    });
};

const givenApiPlayer = function(apiPlayer) {
    apiPlayers.push(apiPlayer);
};

const givenApiAddPlayerReturns = function(apiPlayer) {
    API.doAddPlayer.mockImplementation(cb => cb(apiPlayer));
};

const whenSetPlayersFromApi = function() {
    store.dispatch("players/update", apiPlayers);
};

const whenEnterGame = function() {
    store.dispatch("players/enterGame");
};

const whenLeaveGame = function() {
    store.dispatch("players/leaveGame");
};

const whenAddWasmPlayer = function() {
    store.dispatch("players/addWasmPlayer");
};

const whenRemoveWasmPlayer = function() {
    store.dispatch("players/removeWasmPlayer");
};

const whenRemoveAllClientPlayers = function() {
    store.dispatch("players/removeAllClientPlayers");
};

const whenRemoveClientPlayer = function(id) {
    store.dispatch("players/removeClientPlayer", id);
};

const whenChangeUserPlayerName = function(newName) {
    store.dispatch("players/changeUserPlayerName", newName);
};

const thenPlayerExists = function(id) {
    const players = store.state.players;
    expect(players.byId).toHaveProperty("" + id);
    expect(players.allIds).toContain(id);
};

const thenPlayerDoesNotExist = function(id) {
    const players = store.state.players;
    expect(players.byId).not.toHaveProperty("" + id);
    expect(players.allIds).not.toContain(id);
};

const findPlayer = function(id) {
    return store.getters["players/find"](id);
};
