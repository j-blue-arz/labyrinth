import { mount } from "@vue/test-utils";
import { createTestingPinia } from "@pinia/testing";
import { usePlayersStore } from "@/stores/players.js";
import { useGameStore } from "@/stores/game.js";
import GameMenu from "@/components/GameMenu.vue";
import VMenu from "@/components/VMenu.vue";
import API from "@/services/game-api.js";
import { expect } from "vitest";

import { nextTick } from 'vue'

beforeEach(() => {
    gameMenu = factory();
    playersStore = usePlayersStore();
    gameStore = useGameStore();
    givenNoBots();
    API.fetchComputationMethods.mockImplementation((cb) => cb([]));
    API.doAddBot.mockClear();
    API.removePlayer.mockClear();
    API.changeGame.mockClear();
    API.fetchComputationMethods.mockClear();
});

describe("GameMenu", () => {
    describe("entry leave game", () => {
        it("is visible if user is participating", async () => {
            givenUserIsParticipating();

            await nextTick();

            thenEntryExists("Leave game");
        });

        it("is invisible if user is not participating", async () => {
            givenUserIsNotParticipating();

            await nextTick();

            thenEntryDoesNotExist("Leave game");
        });

        it("calls playersStore to leave game", async () => {
            givenUserIsParticipating();
            await nextTick();

            whenClickInMenu("Leave game");

            thenLeaveGameIsCalledOnPlayersStore();
        });
    });

    describe("entry enter game", () => {
        it("calls method on controller", async () => {
            givenUserIsNotParticipating();
            await nextTick();

            whenClickInMenu("Enter game");

            thenEnterGameIsCalledOnPlayersStore();
        });

        it("is not visible if user participating", async () => {
            givenUserIsParticipating();
            await nextTick();

            thenEntryDoesNotExist("Enter game");
        });
    });

    describe("Add bot submenu", () => {
        it("has entries corresponding to store computation methods", async () => {
            givenComputationMethods(["libminimax-distance", "libexhsearch"]);

            await whenClickInMenu("Add bot..");

            thenEntryDoesNotExist("Minimax (2P)");
            thenEntryExists("Exhaustive Search (1P)");
            thenEntryExists("Minimax (2P) - Distance Heuristic");
        });

        it("calls addBot() on API with computation method", async () => {
            givenComputationMethods(["libexhsearch"]);

            await whenClickInMenu("Add bot..", "Exhaustive Search (1P)");

            expect(API.doAddBot).toHaveBeenCalledWith("libexhsearch");
        });

        it("has WASM entry", async () => {
            givenComputationMethods(["wasm"]);

            await whenClickInMenu("Add bot..");

            thenEntryExists("WASM: Exhaustive Search\u00A0(1P)");
        });

        it("is invisible if game is full", async () => {
            givenGameIsFull();
            await nextTick();

            thenEntryDoesNotExist("Add bot..");
        });

        it("is visible in online mode", async () => {
            givenPlayingOnline();
            givenComputationMethods(["libminimax-distance", "libexhsearch"]);
            await nextTick();

            thenEntryExists("Add bot..");
        });
    });

    describe("Remove bot submenu", () => {
        it("offers all bots for removal", async () => {
            let exhaustiveSearch = createBot(10, "libexhsearch");
            let alphaBeta = createBot(11, "libminimax");
            givenBots([exhaustiveSearch, alphaBeta]);
            await nextTick();

            await whenClickInMenu("Remove bot..");

            thenOneLabelContains("Minimax");
            thenOneLabelContains("Exhaustive Search");
            expectNoLabelContains("WASM: Exhaustive Search");
        });

        it("calls removePlayer() on API with correct player ID for backend players", async () => {
            givenBots([createBot(11, "libexhsearch")]);
            await nextTick();

            await whenClickInMenu("Remove bot..", "11 - Exhaustive Search (1P)");

            expect(API.removePlayer).toHaveBeenCalledWith(11);
        });

        it("calls removeWasmPlayer for WASM player", async () => {
            givenWasmIsParticipating();
            await nextTick();

            await whenClickInMenu("Remove bot..", "3 - WASM: Exhaustive Search");

            thenRemoveWasmPlayerIsCalledOnPlayersStore();
        });

        it("is invisible if no bot exists", async () => {
            givenWasmIsNotParticipating();
            givenBots([]);
            await nextTick();

            thenEntryDoesNotExist("Remove bot..");
        });

        it("is visible if WASM player exists", async () => {
            givenWasmIsParticipating();
            await nextTick();

            thenEntryExists("Remove bot..");
        });
    });

    describe("change game size", () => {
        it("calls changeGame() on API with correct size in online mode", async () => {
            givenPlayingOnline();
            await nextTick();

            await whenClickInMenu("Restart with..", "large size (9)");

            expect(API.changeGame).toHaveBeenCalledWith(9);
        });

        it("calls playOffline on store with correct size", async () => {
            givenPlayingOffline();
            await nextTick();

            await whenClickInMenu("Restart with..", "large size (9)");

            thenPlayOfflineIsCalledOnGameStore(9);
        });
    });

    describe("server connection", () => {
        it("displays 'connect' in offline mode", async () => {
            givenPlayingOffline();
            await nextTick();

            thenEntryExists("Connect to server");
            thenEntryDoesNotExist("Disconnect");
        });

        it("calls 'playOnline' when 'connect' was clicked", async () => {
            givenPlayingOffline();
            await nextTick();

            await whenClickInMenu("Connect to server");

            thenPlayOnlineIsCalledOnGameStore();
        });

        it("calls 'disconnect' in online mode", async () => {
            givenPlayingOnline();
            await nextTick();

            thenEntryExists("Disconnect");
            thenEntryDoesNotExist("Connect to server");
        });

        it("calls 'playOffline' when 'disconnect' was clicked", async () => {
            givenPlayingOnline();
            await nextTick();

            await whenClickInMenu("Disconnect");

            thenPlayOfflineIsCalledOnGameStore();
        });
    });
});

let playersStore;
let gameStore;

let gameMenu;

API.doAddBot = vi.fn();
API.removePlayer = vi.fn();
API.changeGame = vi.fn();
API.fetchComputationMethods = vi.fn();

const factory = function () {
    return mount(GameMenu, {
        global: {
            plugins: [createTestingPinia()],
            directives: {
                "click-outside": {},
            },
        },
    });
};

const givenPlayingOnline = function () {
    gameStore.isOnline = true;
    gameStore.isOffline = false;
};

const givenPlayingOffline = function () {
    gameStore.isOnline = false;
    gameStore.isOffline = true;
};

const givenComputationMethods = function (computationMethods) {
    gameStore.computationMethods = computationMethods;
};

const givenUserIsParticipating = function () {
    playersStore.hasUserPlayer = true;
};

const givenUserIsNotParticipating = function () {
    playersStore.hasUserPlayer = false;
};

const givenGameIsFull = function () {
    playersStore.byId = {
        0: { id: 0 },
        1: { id: 1 },
        2: { id: 2 },
        3: { id: 3 },
    };
    playersStore.allIds = [0, 1, 2, 3];
};

const givenWasmIsParticipating = function () {
    const id = 3;
    const wasmPlayer = {
        id: id,
        isWasm: true,
        name: "",
        pieceIndex: 3,
    };
    playersStore.hasWasmPlayer = true;
    playersStore.wasmPlayerId = id;
    playersStore.find = (playerId) => (playerId === id ? wasmPlayer : null);
};

const givenWasmIsNotParticipating = function () {
    playersStore.hasWasmPlayer = false;
};

const givenBots = function (players) {
    playersStore.bots = players;
};

const givenNoBots = function () {
    playersStore.bots = [];
};

const createBot = function (id, computationMethod) {
    return {
        isBot: true,
        computationMethod: computationMethod,
        id: id,
        pieceIndex: id,
    };
};

const thenOneLabelContains = function (expectedText) {
    const menu = gameMenu.findComponent(VMenu);
    const entries = menu.findAll("li");
    const filtered = entries.filter((entry) => entry.text().includes(expectedText));
    expect(filtered).toHaveLength(1);
};

const expectNoLabelContains = function (expectedText) {
    const menu = gameMenu.findComponent(VMenu);
    const entries = menu.findAll("li");
    const filtered = entries.filter((entry) => entry.text().includes(expectedText));
    expect(filtered).toEqual([]);
};

const whenClickInMenu = async function (...labels) {
    for (let label of labels) {
        await clickInMenu(label);
    }
};

const clickInMenu = async function (label) {
    await findEntryByText(label).trigger("click");
};

const thenLeaveGameIsCalledOnPlayersStore = function () {
    expect(playersStore.leaveGame).toHaveBeenCalledTimes(1);
};

const thenEnterGameIsCalledOnPlayersStore = function() {
    expect(playersStore.enterGame).toHaveBeenCalledTimes(1);
}

const thenRemoveWasmPlayerIsCalledOnPlayersStore = function() {
    expect(playersStore.removeWasmPlayer).toHaveBeenCalledTimes(1);
}

const thenPlayOfflineIsCalledOnGameStore = function(size) {
    if(size) {
        expect(gameStore.playOffline).toHaveBeenCalledWith(size);
    } else {
        expect(gameStore.playOffline).toHaveBeenCalledWith();
    }
    
}

const thenPlayOnlineIsCalledOnGameStore = function() {
    expect(gameStore.playOnline).toHaveBeenCalledTimes(1);
}
expect.extend({
    toExistAsEntry(label) {
        const entries = findEntriesByText(label);
        if (entries.length === 0) {
            return {
                message: () => `expected ${label} to exist as entry`,
                pass: false,
            };
        } else if (entries.length > 1) {
            return {
                message: () => `expected ${label} to to be a unique entry`,
                pass: false,
            };
        } else {
            return {
                message: () => `expected ${label} not to exist as entry`,
                pass: true,
            };
        }
    },
});

const thenEntryExists = function (label) {
    expect(label).toExistAsEntry();
};

const thenEntryDoesNotExist = function (label) {
    expect(findEntriesByText(label)).toEqual([]);
};

function findEntryByText(label) {
    const entries = findEntriesByText(label);
    if (entries.length === 0) {
        throw new Error(`Entry does not exist: "${label}".`);
    }
    return entries.at(0);
}

function findEntriesByText(label) {
    const menu = gameMenu.findComponent(VMenu);
    const entries = menu.findAll("li");
    return entries.filter((entry) => entry.text() === label);
}
