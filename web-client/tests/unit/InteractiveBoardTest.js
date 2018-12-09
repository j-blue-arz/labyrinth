import { shallowMount } from "@vue/test-utils";
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import GameFactory from "@/model/gameFactory";
import { MOVE_ACTION, SHIFT_ACTION } from "@/model/game";

const factory = function(nextAction = MOVE_ACTION) {
    let gameFactory = new GameFactory();
    gameFactory.nextAction = nextAction;
    let game = gameFactory.createGame();
    return shallowMount(InteractiveBoard, {
        propsData: {
            game: game,
            cardSize: 100,
            playerId: 0
        }
    });
};

describe("InteractiveBoard", () => {
    it("rotates leftover maze card when clicked", () => {
        let board = factory(SHIFT_ACTION);
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
        let board = factory(MOVE_ACTION);
        const rotateOperation = jest.spyOn(
            board.props("game").leftoverMazeCard,
            "rotateClockwise"
        );
        let leftoverVMazeCard = board.find({ ref: "leftover" });
        leftoverVMazeCard.trigger("click");
        expect(rotateOperation).toHaveBeenCalledTimes(0);
    });

    it("assigns class 'interaction' on leftover maze card if next action is shift.", () => {
        let board = factory(SHIFT_ACTION);
        let leftoverVMazeCard = board.find({ ref: "leftover" });
        expect(leftoverVMazeCard.classes()).toContain("interaction");
    });

    it("removes class 'interaction' on leftover maze card if next action is move.", () => {
        let board = factory(MOVE_ACTION);
        let leftoverVMazeCard = board.find({ ref: "leftover" });
        expect(leftoverVMazeCard.classes()).not.toContain("interaction");
    });
});
