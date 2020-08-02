import { mount } from "@vue/test-utils";
import { loc } from "@/model/game";
import GameContainer from "@/components/GameContainer.vue";
import VPlayerPiece from "@/components/VPlayerPiece.vue";
import LeftoverMazeCard from "@/components/LeftoverMazeCard.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import flushPromises from "flush-promises";
import { copyObjectStructure, extractIdMatrix } from "./testutils.js";
import GameApi from "@/api/gameApi.js";

jest.useFakeTimers();

var mockFetchState = jest.fn();
var mockAddPlayer = jest.fn();
var mockShift = jest.fn();
var mockMove = jest.fn();
var mockCancel = jest.fn();
var mockErrorWasThrownByCancel = jest.fn();
var mockFetchComputationMethods = jest.fn();
jest.mock("@/api/gameApi.js", () => {
    return jest.fn().mockImplementation(() => {
        return {
            fetchState: mockFetchState,
            doAddPlayer: mockAddPlayer,
            doShift: mockShift,
            doMove: mockMove,
            cancelAllFetches: mockCancel,
            errorWasThrownByCancel: mockErrorWasThrownByCancel,
            fetchComputationMethods: mockFetchComputationMethods
        };
    });
});

beforeEach(() => {
    // Clear all instances and calls to constructor and all methods:
    mockFetchState.mockImplementation(() => Promise.resolve({ data: state }));
    mockAddPlayer.mockImplementation(() => Promise.resolve({ data: { id: 5, pieceIndex: 0 } }));
    mockShift.mockImplementation(() => Promise.resolve({ data: "" }));
    mockMove.mockImplementation(() => Promise.resolve({ data: "" }));
    mockErrorWasThrownByCancel.mockReturnValue(true);
    mockFetchComputationMethods.mockImplementation(() => Promise.resolve([]));
    GameApi.mockClear();
    mockFetchState.mockClear();
    mockAddPlayer.mockClear();
    mockShift.mockClear();
    mockMove.mockClear();
    mockCancel.mockClear();
});

const factory = function() {
    return mount(GameContainer);
};

describe("GameContainer", () => {
    it("sets player id according to result of API call.", async () => {
        let gameContainer = factory();
        expect(mockAddPlayer).toHaveBeenCalledTimes(1);
        await flushPromises();
        expect(gameContainer.vm.userPlayerId).toBe(5);
    });

    it("sets leftover maze card according to fetched state.", async () => {
        let gameContainer = factory();
        await flushPromises();
        expect(mockFetchState).toHaveBeenCalled();
        var leftOverVMazeCard = gameContainer
            .find(InteractiveBoard)
            .find(LeftoverMazeCard)
            .find(VMazeCard);
        var rotation = leftOverVMazeCard.props().mazeCard.rotation;
        expect(rotation).toBe(270);
    });

    it("cancels all fetches on shift operation.", async () => {
        var gameContainer = factory();
        await flushPromises();
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });

        interactiveBoard.vm.$emit("perform-shift", shiftEvent(0, 1, 90));
        expect(mockCancel).toHaveBeenCalledTimes(1);
    });

    it("does not shift before API call returns.", async () => {
        var gameContainer = factory();
        await flushPromises();
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });

        interactiveBoard.vm.$emit("perform-shift", shiftEvent(0, 1, 90));
        expect(mockShift).toHaveBeenCalledTimes(1);
        const shiftOperation = jest.spyOn(gameContainer.vm.$data.game, "shift");
        expect(shiftOperation).toHaveBeenCalledTimes(0);
    });

    it("does shift after API call returns successfully", async () => {
        var gameContainer = factory();
        await flushPromises();
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });
        interactiveBoard.vm.$emit("perform-shift", shiftEvent(0, 1, 90));
        expect(mockShift).toHaveBeenCalledTimes(1);
        const shiftOperation = jest.spyOn(gameContainer.vm.$data.game, "shift");
        await flushPromises();
        expect(shiftOperation).toHaveBeenCalledTimes(1);
    });

    it("shows menu button", () => {
        let gameContainer = factory();
        expect(gameContainer.find(".game-menu__button").exists()).toBe(true);
    });

    it("calls API on move", async () => {
        let stateWithMove = copyObjectStructure(state);
        stateWithMove.nextAction.action = "MOVE";
        mockFetchState.mockImplementation(() => Promise.resolve({ data: stateWithMove }));
        var gameContainer = factory();
        await flushPromises();
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });

        interactiveBoard.vm.$emit("move-piece", moveEvent(0, 3));
        await flushPromises();
        expect(mockMove).toHaveBeenCalledTimes(1);
        let location = mockMove.mock.calls[0][0];
        expect(location.row).toEqual(0);
        expect(location.column).toEqual(3);
    });

    it("moves players when maze card is clicked", async () => {
        let stateWithMove = copyObjectStructure(state);
        stateWithMove.nextAction.action = "MOVE";
        mockFetchState.mockImplementation(() => Promise.resolve({ data: stateWithMove }));
        var gameContainer = factory();
        await flushPromises();
        // player is on (0, 3)
        var interactiveBoard = gameContainer.find({ ref: "interactive-board" });
        interactiveBoard.vm.$emit("move-piece", moveEvent(3, 3));
        await flushPromises();

        var playerCardIds = determineMazeCardIdsWithPlayers(gameContainer);
        expect(playerCardIds.length).toBe(1);
        var idMatrix = extractIdMatrix(gameContainer);
        expect(playerCardIds[0]).toBe(idMatrix[3][3]);
    });
});

/* GENERATED_WITH_LINE_LEFTOVER =
###|#.#|###|#.#|###|###|###|
#..|#.#|...|..#|...|...|..#|
#.#|#.#|#.#|###|#.#|###|#.#|
---------------------------|
###|###|#.#|#.#|###|###|###|
..#|...|#.#|..#|..#|...|#..|
#.#|###|#.#|#.#|#.#|#.#|#.#|
---------------------------|
#.#|###|#.#|#.#|###|###|#.#|
#..|...|#..|#.#|...|...|..#|
#.#|###|#.#|#.#|#.#|###|#.#|
---------------------------|
#.#|###|#.#|#.#|###|#.#|###|
#..|..#|#..|#..|...|#.#|...|
#.#|#.#|###|###|#.#|#.#|###|
---------------------------|
#.#|###|#.#|###|#.#|###|#.#|
#..|..#|...|..#|..#|..#|..#|
#.#|#.#|###|#.#|#.#|#.#|#.#|
---------------------------|
#.#|#.#|###|#.#|###|###|###|
#..|#..|..#|#..|..#|...|...|
#.#|###|#.#|#.#|#.#|###|###|
---------------------------|
#.#|###|#.#|#.#|#.#|#.#|#.#|
#..|..#|...|#..|...|#..|..#|
###|#.#|###|###|###|#.#|###|
---------------------------* */

const determineMazeCardIdsWithPlayers = function(gameContainer) {
    var mazeCardIds = [];
    var vPlayerPieces = gameContainer.find(InteractiveBoard).findAll(VPlayerPiece);
    for (var i = 0; i < vPlayerPieces.length; i++) {
        mazeCardIds.push(
            Number.parseInt(
                vPlayerPieces.at(i).element.parentElement.parentElement.getAttribute("id")
            )
        );
    }
    return mazeCardIds;
};

const shiftEvent = function(row, column, rotation) {
    return { playerId: 5, location: loc(row, column), leftoverRotation: rotation };
};

const moveEvent = function(row, column) {
    return { playerId: 5, targetLocation: loc(row, column) };
};

var state = {
    maze: {
        mazeSize: 7,
        mazeCards: [
            {
                outPaths: "NS",
                id: 49,
                location: null,
                rotation: 270
            },
            {
                outPaths: "NE",
                id: 0,
                location: {
                    column: 0,
                    row: 0
                },
                rotation: 90
            },
            {
                outPaths: "NS",
                id: 1,
                location: {
                    column: 1,
                    row: 0
                },
                rotation: 180
            },
            {
                outPaths: "NES",
                id: 2,
                location: {
                    column: 2,
                    row: 0
                },
                rotation: 90
            },
            {
                outPaths: "NE",
                id: 3,
                location: {
                    column: 3,
                    row: 0
                },
                rotation: 270
            },
            {
                outPaths: "NES",
                id: 4,
                location: {
                    column: 4,
                    row: 0
                },
                rotation: 90
            },
            {
                outPaths: "NS",
                id: 5,
                location: {
                    column: 5,
                    row: 0
                },
                rotation: 90
            },
            {
                outPaths: "NE",
                id: 6,
                location: {
                    column: 6,
                    row: 0
                },
                rotation: 180
            },
            {
                outPaths: "NE",
                id: 7,
                location: {
                    column: 0,
                    row: 1
                },
                rotation: 180
            },
            {
                outPaths: "NS",
                id: 8,
                location: {
                    column: 1,
                    row: 1
                },
                rotation: 90
            },
            {
                outPaths: "NS",
                id: 9,
                location: {
                    column: 2,
                    row: 1
                },
                rotation: 180
            },
            {
                outPaths: "NES",
                id: 10,
                location: {
                    column: 3,
                    row: 1
                },
                rotation: 180
            },
            {
                outPaths: "NE",
                id: 11,
                location: {
                    column: 4,
                    row: 1
                },
                rotation: 180
            },
            {
                outPaths: "NES",
                id: 12,
                location: {
                    column: 5,
                    row: 1
                },
                rotation: 90
            },
            {
                outPaths: "NE",
                id: 13,
                location: {
                    column: 6,
                    row: 1
                },
                rotation: 90
            },
            {
                outPaths: "NES",
                id: 14,
                location: {
                    column: 0,
                    row: 2
                },
                rotation: 0
            },
            {
                outPaths: "NS",
                id: 15,
                location: {
                    column: 1,
                    row: 2
                },
                rotation: 90
            },
            {
                outPaths: "NES",
                id: 16,
                location: {
                    column: 2,
                    row: 2
                },
                rotation: 0
            },
            {
                outPaths: "NS",
                id: 17,
                location: {
                    column: 3,
                    row: 2
                },
                rotation: 180
            },
            {
                outPaths: "NES",
                id: 18,
                location: {
                    column: 4,
                    row: 2
                },
                rotation: 90
            },
            {
                outPaths: "NS",
                id: 19,
                location: {
                    column: 5,
                    row: 2
                },
                rotation: 90
            },
            {
                outPaths: "NES",
                id: 20,
                location: {
                    column: 6,
                    row: 2
                },
                rotation: 180
            },
            {
                outPaths: "NES",
                id: 21,
                location: {
                    column: 0,
                    row: 3
                },
                rotation: 0
            },
            {
                outPaths: "NE",
                id: 22,
                location: {
                    column: 1,
                    row: 3
                },
                rotation: 180
            },
            {
                outPaths: "NE",
                id: 23,
                location: {
                    column: 2,
                    row: 3
                },
                rotation: 0
            },
            {
                outPaths: "NE",
                id: 24,
                location: {
                    column: 3,
                    row: 3
                },
                rotation: 0
            },
            {
                outPaths: "NES",
                id: 25,
                location: {
                    column: 4,
                    row: 3
                },
                rotation: 90
            },
            {
                outPaths: "NS",
                id: 26,
                location: {
                    column: 5,
                    row: 3
                },
                rotation: 180
            },
            {
                outPaths: "NS",
                id: 27,
                location: {
                    column: 6,
                    row: 3
                },
                rotation: 90
            },
            {
                outPaths: "NES",
                id: 28,
                location: {
                    column: 0,
                    row: 4
                },
                rotation: 0
            },
            {
                outPaths: "NE",
                id: 29,
                location: {
                    column: 1,
                    row: 4
                },
                rotation: 180
            },
            {
                outPaths: "NES",
                id: 30,
                location: {
                    column: 2,
                    row: 4
                },
                rotation: 270
            },
            {
                outPaths: "NE",
                id: 31,
                location: {
                    column: 3,
                    row: 4
                },
                rotation: 180
            },
            {
                outPaths: "NES",
                id: 32,
                location: {
                    column: 4,
                    row: 4
                },
                rotation: 180
            },
            {
                outPaths: "NE",
                id: 33,
                location: {
                    column: 5,
                    row: 4
                },
                rotation: 180
            },
            {
                outPaths: "NES",
                id: 34,
                location: {
                    column: 6,
                    row: 4
                },
                rotation: 180
            },
            {
                outPaths: "NES",
                id: 35,
                location: {
                    column: 0,
                    row: 5
                },
                rotation: 0
            },
            {
                outPaths: "NE",
                id: 36,
                location: {
                    column: 1,
                    row: 5
                },
                rotation: 0
            },
            {
                outPaths: "NE",
                id: 37,
                location: {
                    column: 2,
                    row: 5
                },
                rotation: 180
            },
            {
                outPaths: "NES",
                id: 38,
                location: {
                    column: 3,
                    row: 5
                },
                rotation: 0
            },
            {
                outPaths: "NE",
                id: 39,
                location: {
                    column: 4,
                    row: 5
                },
                rotation: 180
            },
            {
                outPaths: "NS",
                id: 40,
                location: {
                    column: 5,
                    row: 5
                },
                rotation: 90
            },
            {
                outPaths: "NS",
                id: 41,
                location: {
                    column: 6,
                    row: 5
                },
                rotation: 90
            },
            {
                outPaths: "NE",
                id: 42,
                location: {
                    column: 0,
                    row: 6
                },
                rotation: 0
            },
            {
                outPaths: "NE",
                id: 43,
                location: {
                    column: 1,
                    row: 6
                },
                rotation: 180
            },
            {
                outPaths: "NES",
                id: 44,
                location: {
                    column: 2,
                    row: 6
                },
                rotation: 270
            },
            {
                outPaths: "NE",
                id: 45,
                location: {
                    column: 3,
                    row: 6
                },
                rotation: 0
            },
            {
                outPaths: "NES",
                id: 46,
                location: {
                    column: 4,
                    row: 6
                },
                rotation: 270
            },
            {
                outPaths: "NES",
                id: 47,
                location: {
                    column: 5,
                    row: 6
                },
                rotation: 0
            },
            {
                outPaths: "NE",
                id: 48,
                location: {
                    column: 6,
                    row: 6
                },
                rotation: 270
            }
        ]
    },
    nextAction: {
        action: "SHIFT",
        playerId: 5
    },
    objectiveMazeCardId: 34,
    players: [
        {
            id: 5,
            isComputerPlayer: false,
            mazeCardId: 3
        }
    ],
    enabledShiftLocations: [
        {
            column: 0,
            row: 3
        },
        {
            column: 6,
            row: 5
        },
        {
            column: 6,
            row: 1
        },
        {
            column: 5,
            row: 0
        },
        {
            column: 0,
            row: 1
        },
        {
            column: 3,
            row: 0
        },
        {
            column: 5,
            row: 6
        },
        {
            column: 1,
            row: 0
        },
        {
            column: 1,
            row: 6
        },
        {
            column: 3,
            row: 6
        },
        {
            column: 6,
            row: 3
        },
        {
            column: 0,
            row: 5
        }
    ]
};
