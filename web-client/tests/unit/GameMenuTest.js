import { mount } from "@vue/test-utils";
import GameMenu from "@/components/GameMenu.vue";
import VMenu from "@/components/VMenu.vue";
import Controller from "@/controllers/controller.js";
import PlayerManager from "@/model/playerManager.js";
import Player from "@/model/player.js";
import Vue from "vue";
import flushPromises from "flush-promises";

beforeEach(() => {
    const playerManager = new PlayerManager(false);
    playerManager.addUserPlayerId(1);
    mockGetPlayerManager.mockReturnValue(playerManager);
    mockGetComputationMethods.mockReturnValue([]);
    mockGetComputerPlayers.mockReturnValue([]);
    mockGetPlayer.mockReturnValue(null);
    mockGetPlayers.mockReturnValue([]);
    // Clear all instances and calls to constructor and all methods:
    Controller.mockClear();
    mockGetComputationMethods.mockClear();
    mockGetPlayerManager.mockClear();
    mockEnterGame.mockClear();
    mockLeaveGame.mockClear();
    mockAddComputer.mockClear();
    mockRemoveComputer.mockClear();
    mockRemoveWasmPlayer.mockClear();
    mockRestartWithSize.mockClear();
    mockAddWasmPlayer.mockClear();
    mockGetComputerPlayers.mockClear();
    mockGetPlayer.mockClear();
    mockGetPlayers.mockClear();
});

describe("GameMenu", () => {
    it("shows menu button", () => {
        let gameMenu = factory();
        expect(gameMenu.find(".game-menu__button").exists()).toBe(true);
    });

    it("menu is initially closed", () => {
        let gameMenu = factory();
        expect(gameMenu.find(".menu").isVisible()).toBe(false);
    });

    it("Opens menu when button is clicked", () => {
        let gameMenu = factory();
        toggleMenu(gameMenu);
        expect(gameMenu.find(".menu").isVisible()).toBe(true);
    });

    it("Closes menu when button is clicked twice", done => {
        let gameMenu = factory();
        toggleMenu(gameMenu);
        toggleMenu(gameMenu);
        Vue.nextTick(() => {
            expect(gameMenu.find(".menu").isVisible()).toBe(false);
            done();
        });
    });

    describe("entry leave game", () => {
        it("is visible if user is participating", () => {
            let gameMenu = factory();
            toggleMenu(gameMenu);
            let entry = gameMenu.find(VMenu).find({ ref: "leave" });
            expect(entry.exists()).toBe(true);
        });

        it("is invisible if user is not participating", () => {
            givenUserIsNotParticipating();
            let gameMenu = factory();
            toggleMenu(gameMenu);

            let entry = gameMenu.find(VMenu).find({ ref: "leave" });
            expect(entry.exists()).toBe(false);
        });

        it("calls method on controller", () => {
            let gameMenu = factory();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "leave");
            expect(mockLeaveGame).toHaveBeenCalled();
        });
    });

    describe("entry enter game", () => {
        it("closes menu", done => {
            givenUserIsNotParticipating();
            let gameMenu = factory();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "enter");
            Vue.nextTick(() => {
                expect(gameMenu.find(".menu").isVisible()).toBe(false);
                done();
            });
        });

        it("calls method on controller", () => {
            givenUserIsNotParticipating();
            let gameMenu = factory();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "enter");
            expect(mockEnterGame).toHaveBeenCalled();
        });

        it("is not visible if user participating", () => {
            let gameMenu = factory();
            toggleMenu(gameMenu);
            let entry = gameMenu.find(VMenu).find({ ref: "enter-game" });
            expect(entry.exists()).toBe(false);
        });
    });

    describe("Add computer submenu", () => {
        it("has entries corresponding to API computation methods", () => {
            givenComputationMethods(["libminimax-distance", "libexhsearch"]);
            let gameMenu = factory();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "add");
            let menu = gameMenu.find(VMenu);
            expect(menu.find({ ref: "add-libminimax-distance" }).exists()).toBe(true);
            expect(menu.find({ ref: "add-libexhsearch" }).exists()).toBe(true);
            expect(menu.find({ ref: "add-alpha-beta" }).exists()).toBe(false);
        });

        it("calls addComputer() on controller with computation method", () => {
            givenComputationMethods(["exhaustive-search"]);
            let gameMenu = factory();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "add");
            clickInMenu(gameMenu, "add-exhaustive-search");
            expect(mockAddComputer).toHaveBeenCalledWith("exhaustive-search");
        });

        it("has WASM entry when there is no WASM player participating", () => {
            givenWasmIsNotParticipating();
            let gameMenu = factory();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "add");
            let menu = gameMenu.find(VMenu);
            expect(menu.find({ ref: "add-wasm" }).exists()).toBe(true);
        });

        it("has no WASM entry when there is already a WASM player participating", () => {
            givenWasmIsParticipating(new Player(7));
            let gameMenu = factory();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "add");
            let menu = gameMenu.find(VMenu);
            expect(menu.find({ ref: "add-wasm" }).exists()).toBe(false);
        });

        it("calls addWasmPlayer for WASM menu entry", () => {
            givenWasmIsNotParticipating();
            let gameMenu = factory();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "add");
            clickInMenu(gameMenu, "add-wasm");
            expect(mockAddWasmPlayer).toHaveBeenCalled();
        });

        it("displays readable labels", async () => {
            givenComputationMethods(["libminimax-distance", "libexhsearch"]);
            givenWasmIsNotParticipating();
            let gameMenu = factory();
            await flushPromises();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "add");
            let menu = gameMenu.find(VMenu);
            let entries = menu.findAll("li");
            let labels = entries.wrappers.map(wrapper => wrapper.text());
            expect(labels).toEqual(
                expect.arrayContaining([
                    "Minimax (2P) - Distance Heuristic",
                    "Exhaustive Search (1P)",
                    "WASM: Exhaustive Search (1P)"
                ])
            );
        });

        it("is invisible if game is full", () => {
            givenGameIsFull();
            let gameMenu = factory();
            toggleMenu(gameMenu);
            let entry = gameMenu.find(VMenu).find({ ref: "add" });
            expect(entry.exists()).toBe(false);
        });
    });

    describe("Remove computer submenu", () => {
        it("offers all computer players for removal", () => {
            let exhaustiveSearch = createComputerPlayer(10, "libexhsearch");
            let alphaBeta = createComputerPlayer(11, "libminimax");
            givenComputerPlayers([exhaustiveSearch, alphaBeta]);
            let gameMenu = factory();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "remove");
            expectMenuContainsLabelContaining(gameMenu, "Minimax");
            expectMenuContainsLabelContaining(gameMenu, "Exhaustive Search");
            expectMenuDoesNotContainLabelContaining(gameMenu, "WASM: Exhaustive Search");
        });

        it("calls removeComputer() on controller with correct player ID for backend players", () => {
            givenComputerPlayers([createComputerPlayer(11, "alpha-beta")]);
            let gameMenu = factory();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "remove");
            clickInMenu(gameMenu, "remove-11");
            expect(mockRemoveComputer).toHaveBeenCalledWith(11);
        });

        it("calls removeWasmPlayer() on controller for WASM player", () => {
            givenWasmIsParticipating(new Player(4));
            let gameMenu = factory();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "remove");
            clickInMenu(gameMenu, "remove-wasm");
            expect(mockRemoveWasmPlayer).toHaveBeenCalled();
        });

        it("is invisible if no computer exists", () => {
            givenComputerPlayers([]);
            let gameMenu = factory();
            toggleMenu(gameMenu);
            let entry = gameMenu.find(VMenu).find({ ref: "remove" });
            expect(entry.exists()).toBe(false);
        });

        it("is visible if WASM player exists", () => {
            givenWasmIsParticipating(new Player(4));
            let gameMenu = factory();
            toggleMenu(gameMenu);
            let entry = gameMenu.find(VMenu).find({ ref: "remove" });
            expect(entry.exists()).toBe(true);
        });
    });

    describe("change game size", () => {
        it("calls restartWithSize() on controller with correct size", () => {
            let gameMenu = factory();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "restart");
            clickInMenu(gameMenu, "restart-9");
            expect(mockRestartWithSize).toHaveBeenCalledWith(9);
        });
    });
});

let mockGetComputationMethods = jest.fn();
let mockGetPlayerManager = jest.fn();
let mockEnterGame = jest.fn();
let mockLeaveGame = jest.fn();
let mockAddComputer = jest.fn();
let mockRemoveComputer = jest.fn();
let mockRemoveWasmPlayer = jest.fn();
let mockRestartWithSize = jest.fn();
let mockAddWasmPlayer = jest.fn();

jest.mock("@/controllers/controller.js", () => {
    return jest.fn().mockImplementation(() => {
        return {
            getComputationMethods: mockGetComputationMethods,
            getPlayerManager: mockGetPlayerManager,
            enterGame: mockEnterGame,
            leaveGame: mockLeaveGame,
            addComputer: mockAddComputer,
            game: mockGame,
            removeComputer: mockRemoveComputer,
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

const mockGetComputerPlayers = jest.fn();
const mockGetPlayer = jest.fn();
const mockGetPlayers = jest.fn();
const mockGame = {
    getComputerPlayers: mockGetComputerPlayers,
    getPlayer: mockGetPlayer,
    getPlayers: mockGetPlayers
};

const givenComputationMethods = function(computationMethods) {
    mockGetComputationMethods.mockReturnValue(computationMethods);
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

const givenComputerPlayers = function(players) {
    mockGetComputerPlayers.mockReturnValue(players);
    mockGetPlayers.mockReturnValue(players);
};

const createComputerPlayer = function(id, computationMethod) {
    let player = new Player(id);
    player.isComputer = true;
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

const toggleMenu = function(gameMenu) {
    gameMenu.find({ ref: "game-menu-button" }).trigger("click");
};

const clickInMenu = function(gameMenu, ref) {
    gameMenu
        .find(VMenu)
        .find({ ref: ref })
        .trigger("click");
};
