import { shallowMount, mount } from "@vue/test-utils";
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import InsertPanels from "@/components/InsertPanels.vue";
import VGameBoard from "@/components/VGameBoard.vue";
import DraggableGameBoard from "@/components/DraggableGameBoard.vue";
import LeftoverMazeCard from "@/components/LeftoverMazeCard.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import { copyObjectStructure } from "./testutils.js";
import Game, { loc } from "@/model/game.js";
import Controller from "@/controllers/controller.js";
import PlayerManager from "../../src/model/playerManager.js";

let mockGetPlayerManager = jest.fn();
let mockPerformShift = jest.fn();
let mockPerformMove = jest.fn();
jest.mock("@/controllers/controller.js", () => {
    return jest.fn().mockImplementation(() => {
        return {
            getPlayerManager: mockGetPlayerManager,
            performShift: mockPerformShift,
            performMove: mockPerformMove
        };
    });
});

const createMockController = function(game) {
    let controller = new Controller(false);
    controller.game = game;
    let playerManager = new PlayerManager();
    playerManager.addUserPlayerId(5);
    mockGetPlayerManager.mockReturnValue(playerManager);
    return controller;
};

const shallowFactory = function(game) {
    let controller = createMockController(game);
    return shallowMount(InteractiveBoard, {
        propsData: {
            controller: controller
        }
    });
};

const factory = function(game) {
    let controller = createMockController(game);
    return mount(InteractiveBoard, {
        propsData: {
            controller: controller
        }
    });
};

function fromStateWithShiftAction() {
    let stateCopy = copyObjectStructure(API_STATE);
    stateCopy.nextAction.action = "SHIFT";
    let game = new Game();
    game.createFromApi(stateCopy);
    return game;
}

function fromStateWithMoveAction() {
    let stateCopy = copyObjectStructure(API_STATE);
    stateCopy.nextAction.action = "MOVE";
    let game = new Game();
    game.createFromApi(stateCopy);
    return game;
}

function findLeftover(board) {
    return board.find(LeftoverMazeCard).find(VMazeCard);
}

beforeEach(() => {
    // Clear all instances and calls to constructor and all methods:
    Controller.mockClear();
    mockGetPlayerManager.mockClear();
    mockPerformShift.mockClear();
    mockPerformMove.mockClear();
});

describe("InteractiveBoard", () => {
    it("rotates leftover maze card when clicked", () => {
        let game = fromStateWithShiftAction();
        let board = factory(game);
        const rotateOperation = jest.spyOn(game.leftoverMazeCard, "rotateClockwise");
        let leftoverVMazeCard = findLeftover(board);
        let oldRotation = leftoverVMazeCard.props().mazeCard.rotation;
        leftoverVMazeCard.trigger("click");
        let newRotation = leftoverVMazeCard.props().mazeCard.rotation;
        expect(newRotation).toBe((oldRotation + 90) % 360);
        expect(rotateOperation).toHaveBeenCalledTimes(1);
    });

    it("does not rotate leftover maze card when next action is move", () => {
        let game = fromStateWithMoveAction();
        let board = factory(game);
        const rotateOperation = jest.spyOn(game.leftoverMazeCard, "rotateClockwise");
        let leftoverVMazeCard = findLeftover(board);
        leftoverVMazeCard.trigger("click");
        expect(rotateOperation).toHaveBeenCalledTimes(0);
    });

    it("assigns class 'interaction' on leftover maze card if next action is shift", () => {
        let board = factory(fromStateWithShiftAction());
        let leftoverVMazeCard = findLeftover(board);
        expect(leftoverVMazeCard.classes()).toContain("maze-card--interactive");
    });

    it("removes class 'interaction' on leftover maze card if next action is move", () => {
        let board = factory(fromStateWithMoveAction());
        let leftoverVMazeCard = findLeftover(board);
        expect(leftoverVMazeCard.classes()).not.toContain("maze-card--interactive");
    });

    it("sets interaction class on reachable maze cards", () => {
        let game = fromStateWithMoveAction();
        let board = factory(game);
        let reachableCardLocations = [loc(0, 2), loc(0, 3), loc(1, 2), loc(2, 2), loc(3, 2)];
        let reachableCardIds = reachableCardLocations.map(
            location => game.getMazeCard(location).id
        );

        let interactiveCardIds = fetchInteractiveCardIds(board);
        expect(interactiveCardIds.length).toBe(reachableCardIds.length);
        expect(interactiveCardIds).toEqual(expect.arrayContaining(reachableCardIds));
    });

    it("does not set interaction class if shift is required", () => {
        let board = factory(fromStateWithShiftAction());
        let interactiveCardIds = fetchInteractiveCardIds(board);
        expect(interactiveCardIds.length).toBe(1); // leftover
    });

    it("calls performMove() on controller when maze card is clicked", () => {
        let game = fromStateWithMoveAction();
        let board = shallowFactory(game);
        let clickedMazeCard = game.mazeCards[0][2];
        board.find(DraggableGameBoard).vm.$emit("player-move", clickedMazeCard);
        expect(mockPerformMove).toHaveBeenCalled();
    });

    it("does not call performMove() if shift is required", () => {
        let game = fromStateWithShiftAction();
        let board = shallowFactory(game);
        let clickedMazeCard = game.mazeCards[0][2];
        board.find(DraggableGameBoard).vm.$emit("player-move", clickedMazeCard);
        expect(mockPerformMove).not.toHaveBeenCalled();
    });

    it("does not call performMove() if clicked maze card is not reachable", () => {
        let game = fromStateWithShiftAction();
        let board = shallowFactory(game);
        let clickedMazeCard = game.mazeCards[0][0];
        board.find(DraggableGameBoard).vm.$emit("player-move", clickedMazeCard);
        expect(mockPerformMove).not.toHaveBeenCalled();
    });

    it("sets interaction on insert panels if shift is required", () => {
        let board = shallowFactory(fromStateWithShiftAction());
        let insertPanels = board.find(InsertPanels);
        expect(insertPanels.props().interaction).toBeTruthy();
    });

    it("does not set interaction on insert panels if move is required", () => {
        let board = shallowFactory(fromStateWithMoveAction());
        let insertPanels = board.find(InsertPanels);
        expect(insertPanels.props().interaction).toBeFalsy();
    });

    it("forwards game to insert panels", () => {
        let game = fromStateWithShiftAction();
        game.disabledShiftLocation = {
            row: 0,
            column: 1
        };
        let board = shallowFactory(game);
        let insertPanels = board.find(InsertPanels);
        expect(insertPanels.props().game).toEqual(game);
    });
});

function fetchInteractiveCardIds(board) {
    let mazeCards = board.findAll(".maze-card");
    let interactiveCardIds = [];
    for (var i = 0; i < mazeCards.length; i++) {
        let card = mazeCards.at(i);
        if (card.classes("maze-card--interactive")) {
            interactiveCardIds.push(parseInt(card.attributes("id")));
        }
    }
    return interactiveCardIds;
}

/* GENERATED_WITH_LINE_LEFTOVER =
###|#.#|###|#.#|###|###|###|
#..|#.#|...|.o#|...|...|..#|
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

var API_STATE = {
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
        action: "MOVE",
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
