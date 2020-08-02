import { mount } from "@vue/test-utils";
import GameMenu from "@/components/GameMenu.vue";
import VMenu from "@/components/VMenu.vue";
import GameApi from "@/api/gameApi.js";
import Player from "@/model/player.js";
import Vue from "vue";
import flushPromises from "flush-promises";

var mockAddComputerPlayer = jest.fn();
var mockRemovePlayer = jest.fn();
var mockFetchComputationMethods = jest.fn();
jest.mock("@/api/gameApi.js", () => {
    return jest.fn().mockImplementation(() => {
        return {
            doAddComputerPlayer: mockAddComputerPlayer,
            removePlayer: mockRemovePlayer,
            fetchComputationMethods: mockFetchComputationMethods
        };
    });
});
mockAddComputerPlayer.mockImplementation(() => Promise.resolve());
mockRemovePlayer.mockImplementation(() => Promise.resolve());
mockFetchComputationMethods.mockImplementation(() => Promise.resolve({ data: [] }));

var mockGetComputerPlayers = jest.fn();
var mockGame = {
    getComputerPlayers: mockGetComputerPlayers
};
mockGetComputerPlayers.mockImplementation(() => [new Player(4, 44), new Player(1, 11)]);

const factory = function(userPlayerId = 7) {
    return mount(GameMenu, {
        propsData: {
            api: new GameApi("foo"),
            game: mockGame,
            userPlayerId: userPlayerId
        }
    });
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

const withComputationMethods = function(computationMethods) {
    mockFetchComputationMethods.mockImplementation(() =>
        Promise.resolve({ data: computationMethods })
    );
};

beforeEach(() => {
    // Clear all instances and calls to constructor and all methods:
    GameApi.mockClear();
    mockAddComputerPlayer.mockClear();
    mockRemovePlayer.mockClear();
    mockGetComputerPlayers.mockClear();
});

describe("GameMenu", () => {
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
        it("emits 'leave-game' event", () => {
            let gameMenu = factory();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "leave");
            expect(gameMenu.emitted("leave-game")).toBeTruthy();
        });

        it("is not visible if user is not participating", () => {
            let gameMenu = factory(-1);
            toggleMenu(gameMenu);
            let entry = gameMenu.find(VMenu).find({ ref: "leave" });
            expect(entry.exists()).toBe(false);
        });
    });

    describe("entry enter game", () => {
        it("closes menu", done => {
            let gameMenu = factory(-1);
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "enter");
            Vue.nextTick(() => {
                expect(gameMenu.find(".menu").isVisible()).toBe(false);
                done();
            });
        });

        it("emits 'enter-game' event", () => {
            let gameMenu = factory(-1);
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "enter");
            expect(gameMenu.emitted("enter-game")).toBeTruthy();
        });

        it("is not visible if user participating", () => {
            let gameMenu = factory();
            toggleMenu(gameMenu);
            let entry = gameMenu.find(VMenu).find({ ref: "enter-game" });
            expect(entry.exists()).toBe(false);
        });
    });

    describe("Add computer submenu", () => {
        it("has entries corresponding to API computation methods", async () => {
            withComputationMethods(["exhaustive-search", "dynamic-libexhsearch"]);
            let gameMenu = factory();
            await flushPromises();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "add");
            let menu = gameMenu.find(VMenu);
            expect(menu.findAll("li").length).toBe(3); // first entry is header
            expect(menu.find({ ref: "add-exhaustive-search" }).exists()).toBe(true);
            expect(menu.find({ ref: "add-dynamic-libexhsearch" }).exists()).toBe(true);
            expect(menu.find({ ref: "add-alpha-beta" }).exists()).toBe(false);
        });

        it("closes menu", async done => {
            withComputationMethods(["alpha-beta", "dynamic-libexhsearch"]);
            let gameMenu = factory();
            await flushPromises();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "add");
            clickInMenu(gameMenu, "add-alpha-beta");
            Vue.nextTick(() => {
                expect(gameMenu.find(".menu").isVisible()).toBe(false);
                done();
            });
        });

        it("calls doAddComputerPlayer() on gameApi with computation method", async () => {
            withComputationMethods(["exhaustive-search"]);
            let gameMenu = factory();
            await flushPromises();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "add");
            clickInMenu(gameMenu, "add-exhaustive-search");
            expect(mockAddComputerPlayer).toHaveBeenCalledTimes(1);
            expect(mockAddComputerPlayer).toHaveBeenCalledWith("exhaustive-search");
        });

        it("Displays readable labels", async () => {
            withComputationMethods(["alpha-beta", "dynamic-libexhsearch"]);
            let gameMenu = factory();
            await flushPromises();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "add");
            let menu = gameMenu.find(VMenu);
            let entries = menu.findAll("li");
            let labels = entries.wrappers.map(wrapper => wrapper.text());
            expect(entries.length).toBe(3); // first entry is header
            expect(labels).toEqual(expect.arrayContaining(["Alpha-Beta", "Library: libexhsearch"]));
        });
    });

    describe("entry remove computer player", () => {
        it("offers all computer players for removal", () => {
            let gameMenu = factory();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "remove");
            let menu = gameMenu.find(VMenu);
            expect(gameMenu.find(".menu").isVisible()).toBe(true);
            let entries = menu.findAll("li");
            expect(entries.length).toBe(3); // first entry is header
            expect(entries.filter(entry => entry.element.textContent.includes("44")).length).toBe(
                1
            );
            expect(entries.filter(entry => entry.element.textContent.includes("11")).length).toBe(
                1
            );
        });

        it("calls removePlayer() on gameApi with correct player ID", () => {
            let gameMenu = factory();
            toggleMenu(gameMenu);
            clickInMenu(gameMenu, "remove");
            clickInMenu(gameMenu, "remove-4");
            expect(mockRemovePlayer).toHaveBeenCalledTimes(1);
            expect(mockRemovePlayer).toHaveBeenCalledWith(4);
        });
    });
});
