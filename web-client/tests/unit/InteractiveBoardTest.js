import { shallowMount, mount } from "@vue/test-utils";
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import VGameBoard from "@/components/VGameBoard.vue";
import { copyObjectStructure } from "./testutils.js";
import Game from "@/model/game.js";
import { loc } from "./testutils.js";

const shallowFactory = function(state = API_STATE) {
    let game = new Game();
    game.createFromApi(state, 5);
    return shallowMount(InteractiveBoard, {
        propsData: {
            game: game,
            cardSize: 100,
            userPlayerId: 5
        }
    });
};

const factory = function(state = API_STATE) {
    let game = new Game();
    game.createFromApi(state, 5);
    return mount(InteractiveBoard, {
        propsData: {
            game: game,
            cardSize: 100,
            userPlayerId: 5
        }
    });
};

function stateWithShiftAction() {
    let stateCopy = copyObjectStructure(API_STATE);
    stateCopy.nextAction.action = "SHIFT";
    return stateCopy;
}

function stateWithMoveAction() {
    let stateCopy = copyObjectStructure(API_STATE);
    stateCopy.nextAction.action = "MOVE";
    return stateCopy;
}

describe("InteractiveBoard", () => {
    it("rotates leftover maze card when clicked", () => {
        let board = shallowFactory(stateWithShiftAction());
        const rotateOperation = jest.spyOn(board.props("game").leftoverMazeCard, "rotateClockwise");
        let leftoverVMazeCard = board.find({ ref: "leftover" });
        let oldRotation = leftoverVMazeCard.props().mazeCard.rotation;
        leftoverVMazeCard.trigger("click");
        let newRotation = leftoverVMazeCard.props().mazeCard.rotation;
        expect(newRotation).toBe((oldRotation + 90) % 360);
        expect(rotateOperation).toHaveBeenCalledTimes(1);
    });

    it("does not rotate leftover maze card when next action is move", () => {
        let board = shallowFactory(stateWithMoveAction());
        const rotateOperation = jest.spyOn(board.props("game").leftoverMazeCard, "rotateClockwise");
        let leftoverVMazeCard = board.find({ ref: "leftover" });
        leftoverVMazeCard.trigger("click");
        expect(rotateOperation).toHaveBeenCalledTimes(0);
    });

    it("assigns class 'interaction' on leftover maze card if next action is shift.", () => {
        let board = shallowFactory(stateWithShiftAction());
        let leftoverVMazeCard = board.find({ ref: "leftover" });
        expect(leftoverVMazeCard.classes()).toContain("interaction");
    });

    it("removes class 'interaction' on leftover maze card if next action is move.", () => {
        let board = shallowFactory(stateWithMoveAction());
        let leftoverVMazeCard = board.find({ ref: "leftover" });
        expect(leftoverVMazeCard.classes()).not.toContain("interaction");
    });

    it("sets interaction class on reachable maze cards", () => {
        let board = factory(stateWithMoveAction());
        let game = board.props().game;
        let reachableCardLocations = [loc(0, 2), loc(0, 3), loc(1, 2), loc(2, 2), loc(3, 2)];
        let reachableCardIds = reachableCardLocations.map(
            location => game.getMazeCard(location).id
        );

        let interactiveCardIds = fetchInteractiveCardIds(board);
        expect(interactiveCardIds.length).toBe(reachableCardIds.length);
        expect(interactiveCardIds).toEqual(expect.arrayContaining(reachableCardIds));
    });

    it("does not set interaction class if shift is required", () => {
        let board = factory(stateWithShiftAction());
        let interactiveCardIds = fetchInteractiveCardIds(board);
        expect(interactiveCardIds.length).toBe(1); // leftover
    });

    it("emits 'move-piece' event when maze card is clicked", () => {
        let board = shallowFactory(stateWithMoveAction());
        let clickedMazeCard = board.props().game.mazeCards[0][2];
        board.find(VGameBoard).vm.$emit("maze-card-clicked", clickedMazeCard);
        expect(board.emitted("move-piece")).toBeTruthy();
    });

    it("does not emit 'move-piece' event if shift is required", () => {
        let board = shallowFactory(stateWithShiftAction());
        let clickedMazeCard = board.props().game.mazeCards[0][2];
        board.find(VGameBoard).vm.$emit("maze-card-clicked", clickedMazeCard);
        expect(board.emitted("move-piece")).toBeFalsy();
    });

    it("does not emit 'move-piece' event if clicked maze card is not reachable", () => {
        let board = shallowFactory(stateWithShiftAction());
        let clickedMazeCard = board.props().game.mazeCards[0][0];
        board.find(VGameBoard).vm.$emit("maze-card-clicked", clickedMazeCard);
        expect(board.emitted("move-piece")).toBeFalsy();
    });
});

function fetchInteractiveCardIds(board) {
    let mazeCards = board.findAll(".maze-card");
    let interactiveCardIds = [];
    for (var i = 0; i < mazeCards.length; i++) {
        let card = mazeCards.at(i);
        if (card.classes("interaction")) {
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
    mazeCards: [
        {
            doors: "NS",
            id: 49,
            location: null,
            rotation: 270
        },
        {
            doors: "NE",
            id: 0,
            location: {
                column: 0,
                row: 0
            },
            rotation: 90
        },
        {
            doors: "NS",
            id: 1,
            location: {
                column: 1,
                row: 0
            },
            rotation: 180
        },
        {
            doors: "NES",
            id: 2,
            location: {
                column: 2,
                row: 0
            },
            rotation: 90
        },
        {
            doors: "NE",
            id: 3,
            location: {
                column: 3,
                row: 0
            },
            rotation: 270
        },
        {
            doors: "NES",
            id: 4,
            location: {
                column: 4,
                row: 0
            },
            rotation: 90
        },
        {
            doors: "NS",
            id: 5,
            location: {
                column: 5,
                row: 0
            },
            rotation: 90
        },
        {
            doors: "NE",
            id: 6,
            location: {
                column: 6,
                row: 0
            },
            rotation: 180
        },
        {
            doors: "NE",
            id: 7,
            location: {
                column: 0,
                row: 1
            },
            rotation: 180
        },
        {
            doors: "NS",
            id: 8,
            location: {
                column: 1,
                row: 1
            },
            rotation: 90
        },
        {
            doors: "NS",
            id: 9,
            location: {
                column: 2,
                row: 1
            },
            rotation: 180
        },
        {
            doors: "NES",
            id: 10,
            location: {
                column: 3,
                row: 1
            },
            rotation: 180
        },
        {
            doors: "NE",
            id: 11,
            location: {
                column: 4,
                row: 1
            },
            rotation: 180
        },
        {
            doors: "NES",
            id: 12,
            location: {
                column: 5,
                row: 1
            },
            rotation: 90
        },
        {
            doors: "NE",
            id: 13,
            location: {
                column: 6,
                row: 1
            },
            rotation: 90
        },
        {
            doors: "NES",
            id: 14,
            location: {
                column: 0,
                row: 2
            },
            rotation: 0
        },
        {
            doors: "NS",
            id: 15,
            location: {
                column: 1,
                row: 2
            },
            rotation: 90
        },
        {
            doors: "NES",
            id: 16,
            location: {
                column: 2,
                row: 2
            },
            rotation: 0
        },
        {
            doors: "NS",
            id: 17,
            location: {
                column: 3,
                row: 2
            },
            rotation: 180
        },
        {
            doors: "NES",
            id: 18,
            location: {
                column: 4,
                row: 2
            },
            rotation: 90
        },
        {
            doors: "NS",
            id: 19,
            location: {
                column: 5,
                row: 2
            },
            rotation: 90
        },
        {
            doors: "NES",
            id: 20,
            location: {
                column: 6,
                row: 2
            },
            rotation: 180
        },
        {
            doors: "NES",
            id: 21,
            location: {
                column: 0,
                row: 3
            },
            rotation: 0
        },
        {
            doors: "NE",
            id: 22,
            location: {
                column: 1,
                row: 3
            },
            rotation: 180
        },
        {
            doors: "NE",
            id: 23,
            location: {
                column: 2,
                row: 3
            },
            rotation: 0
        },
        {
            doors: "NE",
            id: 24,
            location: {
                column: 3,
                row: 3
            },
            rotation: 0
        },
        {
            doors: "NES",
            id: 25,
            location: {
                column: 4,
                row: 3
            },
            rotation: 90
        },
        {
            doors: "NS",
            id: 26,
            location: {
                column: 5,
                row: 3
            },
            rotation: 180
        },
        {
            doors: "NS",
            id: 27,
            location: {
                column: 6,
                row: 3
            },
            rotation: 90
        },
        {
            doors: "NES",
            id: 28,
            location: {
                column: 0,
                row: 4
            },
            rotation: 0
        },
        {
            doors: "NE",
            id: 29,
            location: {
                column: 1,
                row: 4
            },
            rotation: 180
        },
        {
            doors: "NES",
            id: 30,
            location: {
                column: 2,
                row: 4
            },
            rotation: 270
        },
        {
            doors: "NE",
            id: 31,
            location: {
                column: 3,
                row: 4
            },
            rotation: 180
        },
        {
            doors: "NES",
            id: 32,
            location: {
                column: 4,
                row: 4
            },
            rotation: 180
        },
        {
            doors: "NE",
            id: 33,
            location: {
                column: 5,
                row: 4
            },
            rotation: 180
        },
        {
            doors: "NES",
            id: 34,
            location: {
                column: 6,
                row: 4
            },
            rotation: 180
        },
        {
            doors: "NES",
            id: 35,
            location: {
                column: 0,
                row: 5
            },
            rotation: 0
        },
        {
            doors: "NE",
            id: 36,
            location: {
                column: 1,
                row: 5
            },
            rotation: 0
        },
        {
            doors: "NE",
            id: 37,
            location: {
                column: 2,
                row: 5
            },
            rotation: 180
        },
        {
            doors: "NES",
            id: 38,
            location: {
                column: 3,
                row: 5
            },
            rotation: 0
        },
        {
            doors: "NE",
            id: 39,
            location: {
                column: 4,
                row: 5
            },
            rotation: 180
        },
        {
            doors: "NS",
            id: 40,
            location: {
                column: 5,
                row: 5
            },
            rotation: 90
        },
        {
            doors: "NS",
            id: 41,
            location: {
                column: 6,
                row: 5
            },
            rotation: 90
        },
        {
            doors: "NE",
            id: 42,
            location: {
                column: 0,
                row: 6
            },
            rotation: 0
        },
        {
            doors: "NE",
            id: 43,
            location: {
                column: 1,
                row: 6
            },
            rotation: 180
        },
        {
            doors: "NES",
            id: 44,
            location: {
                column: 2,
                row: 6
            },
            rotation: 270
        },
        {
            doors: "NE",
            id: 45,
            location: {
                column: 3,
                row: 6
            },
            rotation: 0
        },
        {
            doors: "NES",
            id: 46,
            location: {
                column: 4,
                row: 6
            },
            rotation: 270
        },
        {
            doors: "NES",
            id: 47,
            location: {
                column: 5,
                row: 6
            },
            rotation: 0
        },
        {
            doors: "NE",
            id: 48,
            location: {
                column: 6,
                row: 6
            },
            rotation: 270
        }
    ],
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
    ]
};
