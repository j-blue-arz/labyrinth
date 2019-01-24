import { mount } from "@vue/test-utils";
import GameMenu from "@/components/GameMenu.vue";
import VMenu from "@/components/VMenu.vue";
import GameApi from "@/api/gameApi.js";
import Player from "@/model/player.js";

var mockRemovePlayers = jest.fn();
var mockReplacePlayer = jest.fn();
jest.mock("@/api/gameApi.js", () => {
    return jest.fn().mockImplementation(() => {
        return {
            removePlayers: mockRemovePlayers,
            replacePlayer: mockReplacePlayer
        };
    });
});
mockRemovePlayers.mockImplementation(() => Promise.resolve());
mockReplacePlayer.mockImplementation(() => Promise.resolve());

var mockGetComputerPlayers = jest.fn();
var mockGame = {
    getComputerPlayers: mockGetComputerPlayers
};
mockGetComputerPlayers.mockImplementation(() => [new Player(4, 44, 444), new Player(1, 11, 111)]);

const factory = function() {
    return mount(GameMenu, {
        propsData: {
            api: new GameApi("foo"),
            game: mockGame,
            userPlayerId: 7
        }
    });
};

beforeEach(() => {
    // Clear all instances and calls to constructor and all methods:
    GameApi.mockClear();
    mockRemovePlayers.mockClear();
    mockReplacePlayer.mockClear();
    mockGetComputerPlayers.mockClear();
});

describe("GameMenu", () => {
    it("menu is initially closed", () => {
        let gameMenu = factory();
        let menu = gameMenu.find(".menu");
        expect(menu.isVisible()).toBe(false);
    });

    it("Opens menu when button is double-clicked", () => {
        let gameMenu = factory();
        let menu = gameMenu.find(".menu");
        gameMenu.find(".game-menu__button").trigger("click", {"ctrlKey": true});
        expect(menu.isVisible()).toBe(true);
    });

    describe("entry close", () => {
        it("closes menu", () => {
            let gameMenu = factory();
            let menu = gameMenu.find(".menu");
            gameMenu.find(".game-menu__button").trigger("click", {"ctrlKey": true});
            gameMenu
                .find(VMenu)
                .find({ ref: "close" })
                .trigger("click");
            expect(menu.isVisible()).toBe(false);
        });
    });

    describe("entry remove", () => {
        it("closes menu", () => {
            let gameMenu = factory();
            let menu = gameMenu.find(".menu");
            gameMenu.find(".game-menu__button").trigger("click", {"ctrlKey": true});
            gameMenu
                .find(VMenu)
                .find({ ref: "remove" })
                .trigger("click");
            expect(menu.isVisible()).toBe(false);
        });

        it("calls removePlayers() on gameApi with computer players' IDs", () => {
            let gameMenu = factory();
            gameMenu.find(".game-menu__button").trigger("click", {"ctrlKey": true});
            gameMenu
                .find(VMenu)
                .find({ ref: "remove" })
                .trigger("click");
            expect(mockRemovePlayers).toHaveBeenCalledTimes(1);
            let argument = mockRemovePlayers.mock.calls[0][0];
            expect(argument).toEqual(expect.arrayContaining([1, 4]));
            expect(argument.length).toBe(2);
        });
    });

    describe("entry exhaustive", () => {
        it("closes menu", () => {
            let gameMenu = factory();
            let menu = gameMenu.find(".menu");
            gameMenu.find(".game-menu__button").trigger("click", {"ctrlKey": true});
            gameMenu
                .find(VMenu)
                .find({ ref: "exhaustive-search" })
                .trigger("click");
            expect(menu.isVisible()).toBe(false);
        });

        it("calls replacePlayer() on gameApi with player's ID and 'exhaustive-search'", () => {
            let gameMenu = factory();
            gameMenu.find(".game-menu__button").trigger("click", {"ctrlKey": true});
            gameMenu
                .find(VMenu)
                .find({ ref: "exhaustive-search" })
                .trigger("click");
            expect(mockReplacePlayer).toHaveBeenCalledTimes(1);
            expect(mockReplacePlayer).toHaveBeenCalledWith(7, "exhaustive-search");
        });
    });

    describe("entry minimax", () => {
        it("closes menu", () => {
            let gameMenu = factory();
            let menu = gameMenu.find(".menu");
            gameMenu.find(".game-menu__button").trigger("click", {"ctrlKey": true});
            gameMenu
                .find(VMenu)
                .find({ ref: "minimax" })
                .trigger("click");
            expect(menu.isVisible()).toBe(false);
        });

        it("calls replacePlayer() on gameApi with player's ID and 'minimax'", () => {
            let gameMenu = factory();
            gameMenu.find(".game-menu__button").trigger("click", {"ctrlKey": true});
            gameMenu
                .find(VMenu)
                .find({ ref: "minimax" })
                .trigger("click");
            expect(mockReplacePlayer).toHaveBeenCalledTimes(1);
            expect(mockReplacePlayer).toHaveBeenCalledWith(7, "minimax");
        });
    });

    describe("entry alpha-beta", () => {
        it("closes menu", () => {
            let gameMenu = factory();
            let menu = gameMenu.find(".menu");
            gameMenu.find(".game-menu__button").trigger("click", {"ctrlKey": true});
            gameMenu
                .find(VMenu)
                .find({ ref: "alpha-beta" })
                .trigger("click");
            expect(menu.isVisible()).toBe(false);
        });

        it("calls replacePlayer() on gameApi with player's ID and 'alpha-beta'", () => {
            let gameMenu = factory();
            gameMenu.find(".game-menu__button").trigger("click", {"ctrlKey": true});
            gameMenu
                .find(VMenu)
                .find({ ref: "alpha-beta" })
                .trigger("click");
            expect(mockReplacePlayer).toHaveBeenCalledTimes(1);
            expect(mockReplacePlayer).toHaveBeenCalledWith(7, "alpha-beta");
        });
    });
});
