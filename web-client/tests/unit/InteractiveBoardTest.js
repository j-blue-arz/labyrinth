import { shallowMount } from "@vue/test-utils";
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import GameFactory from "@/model/gameFactory";
import MOVE_ACTION from "@/model/game";

const factory = function() {
    let game = new GameFactory().createGame();
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
        var board = factory();
        const rotateOperation = jest.spyOn(
            board.props("game").leftoverMazeCard,
            "rotateClockwise"
        );
        var leftOverVMazeCard = board.find({ ref: "leftover" });
        var oldRotation = leftOverVMazeCard.props().mazeCard.rotation;
        leftOverVMazeCard.trigger("click");
        var newRotation = leftOverVMazeCard.props().mazeCard.rotation;
        expect(newRotation).toBe((oldRotation + 90) % 360);
        expect(rotateOperation).toHaveBeenCalledTimes(1);
    });

    it("does not rotate leftover maze card when next action is move", () => {
        var board = factory();
        const rotateOperation = jest.spyOn(
            board.props("game").leftoverMazeCard,
            "rotateClockwise"
        );
        board.props("game").setNextAction(0, MOVE_ACTION);
        var leftOverVMazeCard = board.find({ ref: "leftover" });
        leftOverVMazeCard.trigger("click");
        expect(rotateOperation).toHaveBeenCalledTimes(0);
    });
});
