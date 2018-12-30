import { shallowMount } from "@vue/test-utils";
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import VGameBoard from "@/components/VGameBoard.vue";
import { copyObjectStructure } from "./testutils.js";
import Game from "@/model/game.js";

const factory = function(state = API_STATE) {
    let game = new Game();
    game.createFromApi(state, 5);
    return shallowMount(InteractiveBoard, {
        propsData: {
            game: game,
            cardSize: 100,
            playerId: 5
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
        let board = factory(stateWithShiftAction());
        const rotateOperation = jest.spyOn(
            board.props("game").leftoverMazeCard,
            "rotateClockwise"
        );
        let leftoverVMazeCard = board.find({ ref: "leftover" });
        let oldRotation = leftoverVMazeCard.props().mazeCard.rotation;
        leftoverVMazeCard.trigger("click");
        let newRotation = leftoverVMazeCard.props().mazeCard.rotation;
        expect(newRotation).toBe((oldRotation + 90) % 360);
        expect(rotateOperation).toHaveBeenCalledTimes(1);
    });

    it("does not rotate leftover maze card when next action is move", () => {
        let board = factory(stateWithMoveAction());
        const rotateOperation = jest.spyOn(
            board.props("game").leftoverMazeCard,
            "rotateClockwise"
        );
        let leftoverVMazeCard = board.find({ ref: "leftover" });
        leftoverVMazeCard.trigger("click");
        expect(rotateOperation).toHaveBeenCalledTimes(0);
    });

    it("assigns class 'interaction' on leftover maze card if next action is shift.", () => {
        let board = factory(stateWithShiftAction());
        let leftoverVMazeCard = board.find({ ref: "leftover" });
        expect(leftoverVMazeCard.classes()).toContain("interaction");
    });

    it("removes class 'interaction' on leftover maze card if next action is move.", () => {
        let board = factory(stateWithMoveAction());
        let leftoverVMazeCard = board.find({ ref: "leftover" });
        expect(leftoverVMazeCard.classes()).not.toContain("interaction");
    });

    it("emits 'move-piece' event when maze card is clicked", () => {
        let board = factory(stateWithMoveAction());
        let clickedMazeCard = board.props().game.mazeCards[1][2];
        board.find(VGameBoard).vm.$emit("maze-card-clicked", clickedMazeCard);
        expect(board.emitted("move-piece")).toBeTruthy();
    });

    it("does not emit 'move-piece' event if shift is required", () => {
        let board = factory(stateWithShiftAction());
        let clickedMazeCard = board.props().game.mazeCards[1][2];
        board.find(VGameBoard).vm.$emit("maze-card-clicked", clickedMazeCard);
        expect(board.emitted("move-piece")).toBeFalsy();
    });

    it("does not emit 'move-piece' event if there is not path to clicked maze card", () => {
        let board = factory(stateWithShiftAction());
        let clickedMazeCard = board.props().game.mazeCards[0][0];
        board.find(VGameBoard).vm.$emit("maze-card-clicked", clickedMazeCard);
        expect(board.emitted("move-piece")).toBeFalsy();
    });
});

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
