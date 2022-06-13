import { mount } from "@vue/test-utils";
import { createTestStore, GET_GAME_STATE_RESULT_FOR_N_3 } from "../testfixtures.js";
import VGameBoard from "@/components/VGameBoard.vue";
import VMazeCard from "@/components/VMazeCard.vue";

const findLowestPositionOfMazeCard = function (vGameBoard, dimension) {
    var vMazeCards = vGameBoard.findAll(VMazeCard);
    var min = Number.MAX_VALUE;
    for (var i = 0; i < vMazeCards.length; i++) {
        var value = parseInt(vMazeCards.at(i).element.getAttribute(dimension));
        if (value < min) min = value;
    }
    return min;
};

describe("VGameBoard", () => {
    it("renders all VMazeCard components", () => {
        givenVGameBoard();

        expect(vGameBoard.findAll(VMazeCard).length).toBe(3 * 3);
    });

    it("renders leftmost v-maze-card exactly at 0", () => {
        givenVGameBoard();

        var xPos = findLowestPositionOfMazeCard(vGameBoard, "x");
        expect(xPos).toBe(0);
    });

    it("renders topmost v-maze-card exactly at 0", () => {
        givenVGameBoard();
        var yPos = findLowestPositionOfMazeCard(vGameBoard, "y");
        expect(yPos).toBe(0);
    });
});

let vGameBoard;
let store;

function givenVGameBoard() {
    store = createTestStore(GET_GAME_STATE_RESULT_FOR_N_3);
    vGameBoard = mount(VGameBoard, {
        global: {
            plugins: [store],
        },
    });
}
