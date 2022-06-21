import { mount } from "@vue/test-utils";
import playersConfig from "@/store/modules/players.js";
import GameMenu from "@/components/GameMenu.vue";
import VMenu from "@/components/VMenu.vue";
import { computationMethodLabel } from "@/model/player.js";
import API from "@/services/game-api.js";

beforeEach(() => {
    mockStore = createMockStore();
    givenNoBots();
    API.fetchComputationMethods.mockImplementation((cb) => cb([]));
    API.doAddBot.mockClear();
    API.removePlayer.mockClear();
    API.changeGame.mockClear();
    API.fetchComputationMethods.mockClear();
});

describe("GameMenu", () => {
    describe("entry leave game", () => {
        it("is visible if user is participating", () => {
            givenUserIsParticipating();

            whenGameMenuIsCreated();

            thenEntryExists("Leave game");
        });

        it("is invisible if user is not participating", () => {
            givenUserIsNotParticipating();

            whenGameMenuIsCreated();

            thenEntryDoesNotExist("Leave game");
        });

        it("dispatches leaveGame", () => {
            givenUserIsParticipating();
            givenGameMenu();

            whenClickInMenu("Leave game");

            thenDispatchWas("players/leaveGame");
        });
    });

    describe("entry enter game", () => {
        it("calls method on controller", () => {
            givenUserIsNotParticipating();
            givenGameMenu();

            whenClickInMenu("Enter game");

            thenDispatchWas("players/enterGame");
        });

        it("is not visible if user participating", () => {
            givenUserIsParticipating();

            whenGameMenuIsCreated();

            thenEntryDoesNotExist("Enter game");
        });
    });

    describe("Add bot submenu", () => {
        it("has entries corresponding to store computation methods", async () => {
            givenComputationMethods(["libminimax-distance", "libexhsearch"]);
            givenGameMenu();

            await whenClickInMenu("Add bot..");

            thenEntryDoesNotExist("Minimax (2P)");
            thenEntryExists("Exhaustive Search (1P)");
            thenEntryExists("Minimax (2P) - Distance Heuristic");
        });

        it("calls addBot() on API with computation method", async () => {
            givenComputationMethods(["libexhsearch"]);
            givenGameMenu();

            await whenClickInMenu("Add bot..", "Exhaustive Search (1P)");

            expect(API.doAddBot).toHaveBeenCalledWith("libexhsearch");
        });

        it("has WASM entry", async () => {
            givenComputationMethods(["wasm"]);
            givenGameMenu();

            await whenClickInMenu("Add bot..");

            thenEntryExists("WASM: Exhaustive Search\u00A0(1P)");
        });

        it("is invisible if game is full", () => {
            givenGameIsFull();

            whenGameMenuIsCreated();

            thenEntryDoesNotExist("add");
        });
    });

    describe("Remove bot submenu", () => {
        it("offers all bots for removal", async () => {
            let exhaustiveSearch = createBot(10, "libexhsearch");
            let alphaBeta = createBot(11, "libminimax");
            givenBots([exhaustiveSearch, alphaBeta]);
            givenGameMenu();

            await whenClickInMenu("Remove bot..");

            thenOneLabelContains("Minimax");
            thenOneLabelContains("Exhaustive Search");
            expectNoLabelContains("WASM: Exhaustive Search");
        });

        it("calls removePlayer() on API with correct player ID for backend players", async () => {
            givenBots([createBot(11, "libexhsearch")]);
            givenGameMenu();

            await whenClickInMenu("Remove bot..", "11 - Exhaustive Search (1P)");

            expect(API.removePlayer).toHaveBeenCalledWith(11);
        });

        it("dispatches removeWasmPlayer for WASM player", async () => {
            givenWasmIsParticipating();
            givenGameMenu();

            await whenClickInMenu("Remove bot..", "3 - WASM: Exhaustive Search");

            thenDispatchWas("players/removeWasmPlayer");
        });

        it("is invisible if no bot exists", () => {
            givenWasmIsNotParticipating();
            givenBots([]);

            whenGameMenuIsCreated();

            thenEntryDoesNotExist("Remove bot..");
        });

        it("is visible if WASM player exists", () => {
            givenWasmIsParticipating();

            whenGameMenuIsCreated();

            thenEntryExists("Remove bot..");
        });
    });

    describe("change game size", () => {
        it("calls changeGame() on API with correct size in online mode", async () => {
            givenPlayingOnline();
            givenGameMenu();

            await whenClickInMenu("Restart with..", "large size (9)");

            expect(API.changeGame).toHaveBeenCalledWith(9);
        });

        it("dispatches change of size on store with correct size in offline mode", async () => {
            givenPlayingOffline();
            givenGameMenu();

            await whenClickInMenu("Restart with..", "large size (9)");

            thenDispatchWas("game/playOffline", 9);
        });
    });

    describe("server connection", () => {
        it("displays 'connect' in offline mode", () => {
            givenPlayingOffline();

            whenGameMenuIsCreated();

            thenEntryExists("Connect to server");
            thenEntryDoesNotExist("Disconnect");
        });

        it("dispatches 'playOnline' when 'connect' was clicked", async () => {
            givenPlayingOffline();
            givenGameMenu();

            await whenClickInMenu("Connect to server");

            thenDispatchWas("game/playOnline");
        });

        it("displays 'disconnect' in online mode", async () => {
            givenPlayingOnline();

            await whenGameMenuIsCreated();

            thenEntryExists("Disconnect");
            thenEntryDoesNotExist("Connect to server");
        });

        it("dispatches 'playOffline' when 'disconnect' was clicked", async () => {
            givenPlayingOnline();
            givenGameMenu();

            await whenClickInMenu("Disconnect");

            thenDispatchWas("game/playOffline");
        });
    });
});

const { state } = playersConfig;

const createMockStore = function () {
    return {
        dispatch: jest.fn(),
        state: {
            players: state(),
        },
        getters: {},
    };
};

let mockStore = createMockStore();

let gameMenu;

API.doAddBot = jest.fn();
API.removePlayer = jest.fn();
API.changeGame = jest.fn();
API.fetchComputationMethods = jest.fn();

const factory = function () {
    return mount(GameMenu, {
        global: {
            mocks: {
                $store: mockStore,
            },
            directives: {
                "click-outside": {},
            },
        },
    });
};

const givenGameMenu = function () {
    gameMenu = factory();
};

const whenGameMenuIsCreated = function () {
    gameMenu = factory();
};

const givenPlayingOnline = function () {
    mockStore.getters["game/isOnline"] = true;
    mockStore.getters["game/isOffline"] = false;
};

const givenPlayingOffline = function () {
    mockStore.getters["game/isOnline"] = false;
    mockStore.getters["game/isOffline"] = true;
};

const givenComputationMethods = function (computationMethods) {
    mockStore.getters["game/computationMethods"] = computationMethods;
};

const givenUserIsParticipating = function () {
    mockStore.getters["players/hasUserPlayer"] = true;
};

const givenUserIsNotParticipating = function () {
    mockStore.getters["players/hasUserPlayer"] = false;
};

const givenGameIsFull = function () {
    mockStore.state.players.byId = {
        0: { id: 0 },
        1: { id: 1 },
        2: { id: 2 },
        3: { id: 3 },
    };
    mockStore.state.players.allIds = [0, 1, 2, 3];
};

const givenWasmIsParticipating = function () {
    const id = 3;
    const wasmPlayer = {
        id: id,
        isWasm: true,
        name: "",
        pieceIndex: 3,
    };
    mockStore.getters["players/hasWasmPlayer"] = true;
    mockStore.getters["players/wasmPlayerId"] = id;
    mockStore.getters["players/find"] = (playerId) => (playerId === id ? wasmPlayer : null);
};

const givenWasmIsNotParticipating = function () {
    mockStore.getters["players/hasWasmPlayer"] = false;
};

const givenBots = function (players) {
    mockStore.getters["players/bots"] = players;
};

const givenNoBots = function () {
    mockStore.getters["players/bots"] = [];
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

const thenDispatchWas = function (expected, arg) {
    if (arg) {
        expect(mockStore.dispatch).toHaveBeenCalledWith(expected, arg);
    } else {
        expect(mockStore.dispatch).toHaveBeenCalledWith(expected);
    }
};

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
