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

            thenEntryExists("leave");
        });

        it("is invisible if user is not participating", () => {
            givenUserIsNotParticipating();

            whenGameMenuIsCreated();

            thenEntryDoesNotExist("leave");
        });

        it("dispatches leaveGame", () => {
            givenUserIsParticipating();
            givenGameMenu();

            whenClickInMenu("leave");

            thenDispatchWas("players/leaveGame");
        });
    });

    describe("entry enter game", () => {
        it("calls method on controller", () => {
            givenUserIsNotParticipating();
            givenGameMenu();

            whenClickInMenu("enter");

            thenDispatchWas("players/enterGame");
        });

        it("is not visible if user participating", () => {
            whenGameMenuIsCreated();

            thenEntryDoesNotExist("enter-game");
        });
    });

    describe("Add bot submenu", () => {
        it("has entries corresponding to store computation methods", () => {
            givenComputationMethods(["libminimax-distance", "libexhsearch"]);
            givenGameMenu();

            whenClickInMenu("add");

            thenEntryDoesNotExist("add-alpha-beta");
            thenEntryExists("add-libexhsearch");
            thenEntryExists("add-libminimax-distance");
        });

        it("calls addBot() on API with computation method", () => {
            givenComputationMethods(["exhaustive-search"]);
            givenGameMenu();

            whenClickInMenu("add", "add-exhaustive-search");

            expect(API.doAddBot).toHaveBeenCalledWith("exhaustive-search");
        });

        it("has no WASM entry when there is already a WASM player participating", () => {
            givenComputationMethods(["exhaustive-search"]);
            givenGameMenu();

            whenClickInMenu("add");

            thenEntryDoesNotExist("add-wasm");
        });

        it("displays readable labels", () => {
            givenComputationMethods(["libminimax-distance", "libexhsearch", "wasm"]);
            givenWasmIsNotParticipating();
            givenGameMenu();

            whenClickInMenu("add");

            thenReadableLabelsAreDisplayed();
        });

        it("is invisible if game is full", () => {
            givenGameIsFull();

            whenGameMenuIsCreated();

            thenEntryDoesNotExist("add");
        });
    });

    describe("Remove bot submenu", () => {
        it("offers all bots for removal", () => {
            let exhaustiveSearch = createBot(10, "libexhsearch");
            let alphaBeta = createBot(11, "libminimax");
            givenBots([exhaustiveSearch, alphaBeta]);
            givenGameMenu();

            whenClickInMenu("remove");

            thenOneLabelContains("Minimax");
            thenOneLabelContains("Exhaustive Search");
            expectNoLabelContains("WASM: Exhaustive Search");
        });

        it("calls removePlayer() on API with correct player ID for backend players", () => {
            givenBots([createBot(11, "alpha-beta")]);
            givenGameMenu();

            whenClickInMenu("remove", "remove-11");

            expect(API.removePlayer).toHaveBeenCalledWith(11);
        });

        it("dispatches removeWasmPlayer for WASM player", () => {
            givenWasmIsParticipating();
            givenGameMenu();

            whenClickInMenu("remove", "remove-wasm");

            thenDispatchWas("players/removeWasmPlayer");
        });

        it("is invisible if no bot exists", () => {
            givenBots([]);

            whenGameMenuIsCreated();

            thenEntryDoesNotExist("remove");
        });

        it("is visible if WASM player exists", () => {
            givenWasmIsParticipating();

            whenGameMenuIsCreated();

            thenEntryExists("remove");
        });
    });

    describe("change game size", () => {
        it("calls changeGame() on API with correct size in online mode", () => {
            givenPlayingOnline();
            givenGameMenu();

            whenClickInMenu("restart", "restart-9");

            expect(API.changeGame).toHaveBeenCalledWith(9);
        });

        it("dispatches change of size on store with correct size in offline mode", () => {
            givenPlayingOffline();
            givenGameMenu();

            whenClickInMenu("restart", "restart-9");

            thenDispatchWas("game/playOffline", 9);
        });
    });

    describe("server connection", () => {
        it("displays 'connect' in offline mode", () => {
            givenPlayingOffline();

            whenGameMenuIsCreated();

            thenEntryExists("connect");
            thenEntryDoesNotExist("disconnect");
        });

        it("dispatches 'playOnline' when 'connect' was clicked", async () => {
            givenPlayingOffline();
            givenGameMenu();

            await whenClickInMenu("connect");

            thenDispatchWas("game/playOnline");
        });

        it("displays 'disconnect' in online mode", async () => {
            givenPlayingOnline();

            await whenGameMenuIsCreated();

            thenEntryExists("disconnect");
            thenEntryDoesNotExist("connect");
        });

        it("dispatches 'playOffline' when 'disconnect' was clicked", async () => {
            givenPlayingOnline();
            givenGameMenu();

            await whenClickInMenu("disconnect");

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
    let menu = gameMenu.findComponent(VMenu);
    expect(gameMenu.find(".menu").isVisible()).toBe(true);
    let entries = menu.findAll("li").wrappers;
    expect(entries.find((entry) => entry.text().includes(expectedText))).not.toBeUndefined();
};

const expectNoLabelContains = function (expectedText) {
    let menu = gameMenu.findComponent(VMenu);
    expect(gameMenu.find(".menu").isVisible()).toBe(true);
    let entries = menu.findAll("li").wrappers;
    expect(entries.find((entry) => entry.text().includes(expectedText))).toBeUndefined();
};

const whenClickInMenu = async function (...refs) {
    await refs.forEach((ref) => {
        clickInMenu(ref);
    });
};

const clickInMenu = async function (ref) {
    await gameMenu.findComponent(VMenu).find({ ref: ref }).trigger("click");
};

const thenDispatchWas = function (expected, arg) {
    if (arg) {
        expect(mockStore.dispatch).toHaveBeenCalledWith(expected, arg);
    } else {
        expect(mockStore.dispatch).toHaveBeenCalledWith(expected);
    }
};

const thenEntryExists = function (ref) {
    let entry = gameMenu.findComponent(VMenu).find({ ref: ref });
    expect(entry.exists()).toBe(true);
};

const thenEntryDoesNotExist = function (ref) {
    let entry = gameMenu.findComponent(VMenu).find({ ref: ref });
    expect(entry.exists()).toBe(false);
};
function thenReadableLabelsAreDisplayed() {
    let menu = gameMenu.findComponent(VMenu);
    let entries = menu.findAll("li");
    let labels = entries.wrappers.map((wrapper) => wrapper.text());
    expect(labels).toEqual(
        expect.arrayContaining([
            computationMethodLabel("libminimax-distance"),
            computationMethodLabel("libexhsearch"),
            "WASM: Exhaustive Search\u00A0(1P)",
        ])
    );
}
