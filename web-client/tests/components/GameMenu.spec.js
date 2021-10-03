import { mount } from "@vue/test-utils";
import GameMenu from "@/components/GameMenu.vue";
import VMenu from "@/components/VMenu.vue";
import Controller from "@/controllers/controller.js";
import PlayerManager from "@/model/playerManager.js";
import Player from "@/model/player.js";
import API from "@/services/game-api.js";

beforeEach(() => {
    const playerManager = new PlayerManager();
    playerManager.addUserPlayerId(1);
    mockGetPlayerManager.mockReturnValue(playerManager);
    API.fetchComputationMethods.mockImplementation(cb => cb([]));
    mockGetBots.mockReturnValue([]);
    mockGetPlayer.mockReturnValue(null);
    mockGetPlayers.mockReturnValue([]);
    // Clear all instances and calls to constructor and all methods:
    Controller.mockClear();
    mockGetPlayerManager.mockClear();
    mockEnterGame.mockClear();
    mockLeaveGame.mockClear();
    mockAddBot.mockClear();
    mockRemoveBot.mockClear();
    mockRemoveWasmPlayer.mockClear();
    mockRestartWithSize.mockClear();
    mockAddWasmPlayer.mockClear();
    mockGetBots.mockClear();
    mockGetPlayer.mockClear();
    mockGetPlayers.mockClear();
    API.fetchComputationMethods.mockClear();
});

describe("GameMenu", () => {
    describe("entry leave game", () => {
        it("is visible if user is participating", () => {
            let gameMenu = factory();
            let entry = gameMenu.find(VMenu).find({ ref: "leave" });
            expect(entry.exists()).toBe(true);
        });

        it("is invisible if user is not participating", () => {
            givenUserIsNotParticipating();
            let gameMenu = factory();

            let entry = gameMenu.find(VMenu).find({ ref: "leave" });
            expect(entry.exists()).toBe(false);
        });

        it("calls method on controller", () => {
            let gameMenu = factory();
            clickInMenu(gameMenu, "leave");
            expect(mockLeaveGame).toHaveBeenCalled();
        });
    });

    describe("entry enter game", () => {
        it("calls method on controller", () => {
            givenUserIsNotParticipating();
            let gameMenu = factory();
            clickInMenu(gameMenu, "enter");
            expect(mockEnterGame).toHaveBeenCalled();
        });

        it("is not visible if user participating", () => {
            let gameMenu = factory();
            let entry = gameMenu.find(VMenu).find({ ref: "enter-game" });
            expect(entry.exists()).toBe(false);
        });
    });

    describe("Add bot submenu", () => {
        it("has entries corresponding to API computation methods", () => {
            givenComputationMethods(["libminimax-distance", "libexhsearch"]);
            let gameMenu = factory();
            clickInMenu(gameMenu, "add");
            let menu = gameMenu.find(VMenu);
            expect(menu.find({ ref: "add-libminimax-distance" }).exists()).toBe(true);
            expect(menu.find({ ref: "add-libexhsearch" }).exists()).toBe(true);
            expect(menu.find({ ref: "add-alpha-beta" }).exists()).toBe(false);
        });

        it("calls addBot() on controller with computation method", () => {
            givenComputationMethods(["exhaustive-search"]);
            let gameMenu = factory();
            clickInMenu(gameMenu, "add");
            clickInMenu(gameMenu, "add-exhaustive-search");
            expect(mockAddBot).toHaveBeenCalledWith("exhaustive-search");
        });

        it("has WASM entry when there is no WASM player participating", () => {
            givenWasmIsNotParticipating();
            let gameMenu = factory();
            clickInMenu(gameMenu, "add");
            let menu = gameMenu.find(VMenu);
            expect(menu.find({ ref: "add-wasm" }).exists()).toBe(true);
        });

        it("has no WASM entry when there is already a WASM player participating", () => {
            givenWasmIsParticipating(new Player(7));
            let gameMenu = factory();
            clickInMenu(gameMenu, "add");
            let menu = gameMenu.find(VMenu);
            expect(menu.find({ ref: "add-wasm" }).exists()).toBe(false);
        });

        it("calls addWasmPlayer for WASM menu entry", () => {
            givenWasmIsNotParticipating();
            let gameMenu = factory();
            clickInMenu(gameMenu, "add");
            clickInMenu(gameMenu, "add-wasm");
            expect(mockAddWasmPlayer).toHaveBeenCalled();
        });

        it("displays readable labels", () => {
            givenComputationMethods(["libminimax-distance", "libexhsearch"]);
            givenWasmIsNotParticipating();
            let gameMenu = factory();
            clickInMenu(gameMenu, "add");
            let menu = gameMenu.find(VMenu);
            let entries = menu.findAll("li");
            let labels = entries.wrappers.map(wrapper => wrapper.text());
            expect(labels).toEqual(
                expect.arrayContaining([
                    Player.computationMethodLabel("libminimax-distance"),
                    Player.computationMethodLabel("libexhsearch"),
                    "WASM: Exhaustive Search\u00A0(1P)"
                ])
            );
        });

        it("is invisible if game is full", () => {
            givenGameIsFull();
            let gameMenu = factory();
            let entry = gameMenu.find(VMenu).find({ ref: "add" });
            expect(entry.exists()).toBe(false);
        });
    });

    describe("Remove bot submenu", () => {
        it("offers all bots for removal", () => {
            let exhaustiveSearch = createBot(10, "libexhsearch");
            let alphaBeta = createBot(11, "libminimax");
            givenBots([exhaustiveSearch, alphaBeta]);
            let gameMenu = factory();
            clickInMenu(gameMenu, "remove");
            expectMenuContainsLabelContaining(gameMenu, "Minimax");
            expectMenuContainsLabelContaining(gameMenu, "Exhaustive Search");
            expectMenuDoesNotContainLabelContaining(gameMenu, "WASM: Exhaustive Search");
        });

        it("calls removeBot() on controller with correct player ID for backend players", () => {
            givenBots([createBot(11, "alpha-beta")]);
            let gameMenu = factory();
            clickInMenu(gameMenu, "remove");
            clickInMenu(gameMenu, "remove-11");
            expect(mockRemoveBot).toHaveBeenCalledWith(11);
        });

        it("calls removeWasmPlayer() on controller for WASM player", () => {
            givenWasmIsParticipating(new Player(4));
            let gameMenu = factory();
            clickInMenu(gameMenu, "remove");
            clickInMenu(gameMenu, "remove-wasm");
            expect(mockRemoveWasmPlayer).toHaveBeenCalled();
        });

        it("is invisible if no bot exists", () => {
            givenBots([]);
            let gameMenu = factory();
            let entry = gameMenu.find(VMenu).find({ ref: "remove" });
            expect(entry.exists()).toBe(false);
        });

        it("is visible if WASM player exists", () => {
            givenWasmIsParticipating(new Player(4));
            let gameMenu = factory();
            let entry = gameMenu.find(VMenu).find({ ref: "remove" });
            expect(entry.exists()).toBe(true);
        });
    });

    describe("change game size", () => {
        it("calls restartWithSize() on controller with correct size", () => {
            let gameMenu = factory();
            clickInMenu(gameMenu, "restart");
            clickInMenu(gameMenu, "restart-9");
            expect(mockRestartWithSize).toHaveBeenCalledWith(9);
        });
    });
});

let mockGetPlayerManager = jest.fn();
let mockEnterGame = jest.fn();
let mockLeaveGame = jest.fn();
let mockAddBot = jest.fn();
let mockRemoveBot = jest.fn();
let mockRemoveWasmPlayer = jest.fn();
let mockRestartWithSize = jest.fn();
let mockAddWasmPlayer = jest.fn();
API.fetchComputationMethods = jest.fn();

jest.mock("@/controllers/controller.js", () => {
    return jest.fn().mockImplementation(() => {
        return {
            playerManager: mockGetPlayerManager(),
            enterGame: mockEnterGame,
            leaveGame: mockLeaveGame,
            addBot: mockAddBot,
            game: mockGame,
            removeBot: mockRemoveBot,
            removeWasmPlayer: mockRemoveWasmPlayer,
            restartWithSize: mockRestartWithSize,
            addWasmPlayer: mockAddWasmPlayer
        };
    });
});

const factory = function() {
    let controller = new Controller(false);
    return mount(GameMenu, {
        propsData: {
            controller: controller
        }
    });
};

const mockGetBots = jest.fn();
const mockGetPlayer = jest.fn();
const mockGetPlayers = jest.fn();
const mockGame = {
    getBots: mockGetBots,
    getPlayer: mockGetPlayer,
    getPlayers: mockGetPlayers
};

const givenComputationMethods = function(computationMethods) {
    API.fetchComputationMethods.mockImplementation(cb => cb(computationMethods));
};

const givenUserIsNotParticipating = function() {
    let playerManager = mockGetPlayerManager();
    playerManager.removeUserPlayer();
};

const givenWasmIsParticipating = function(wasmPlayer) {
    let playerManager = mockGetPlayerManager();
    playerManager.addWasmPlayerId(wasmPlayer.id);
    mockGetPlayer.mockImplementation(playerId => {
        if (playerId === wasmPlayer.id) {
            return wasmPlayer;
        } else {
            return null;
        }
    });
    mockGetPlayers.mockReturnValue([wasmPlayer]);
};

const givenGameIsFull = function() {
    mockGetPlayers.mockReturnValue([new Player(0), new Player(1), new Player(2), new Player(3)]);
};

const givenWasmIsNotParticipating = function() {
    let playerManager = mockGetPlayerManager();
    playerManager.removeWasmPlayer();
};

const givenBots = function(players) {
    mockGetBots.mockReturnValue(players);
    mockGetPlayers.mockReturnValue(players);
};

const createBot = function(id, computationMethod) {
    let player = new Player(id);
    player.isBot = true;
    player.computationMethod = computationMethod;
    return player;
};

const expectMenuContainsLabelContaining = function(gameMenu, expectedText) {
    let menu = gameMenu.find(VMenu);
    expect(gameMenu.find(".menu").isVisible()).toBe(true);
    let entries = menu.findAll("li").wrappers;
    expect(entries.find(entry => entry.text().includes(expectedText))).not.toBeUndefined();
};

const expectMenuDoesNotContainLabelContaining = function(gameMenu, expectedText) {
    let menu = gameMenu.find(VMenu);
    expect(gameMenu.find(".menu").isVisible()).toBe(true);
    let entries = menu.findAll("li").wrappers;
    expect(entries.find(entry => entry.text().includes(expectedText))).toBeUndefined();
};

const clickInMenu = function(gameMenu, ref) {
    gameMenu
        .find(VMenu)
        .find({ ref: ref })
        .trigger("click");
};
