import VGameBoard from "@/components/VGameBoard.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import { createTestingPinia } from "@pinia/testing";
import { mount } from "@vue/test-utils";
import { createTestStores, GET_GAME_STATE_RESULT_FOR_N_3 } from "../testfixtures.js";
import { nextTick } from "vue";

const findLowestPositionOfMazeCard = function (vGameBoard, dimension) {
    var vMazeCards = vGameBoard.findAllComponents(VMazeCard);
    var min = Number.MAX_VALUE;
    for (var i = 0; i < vMazeCards.length; i++) {
        var value = parseInt(vMazeCards.at(i).element.getAttribute(dimension));
        if (value < min) min = value;
    }
    return min;
};

describe("VGameBoard", () => {
    it("renders all VMazeCard components", async () => {
        givenVGameBoard();

        await nextTick();

        expect(vGameBoard.findAllComponents(VMazeCard).length).toBe(3 * 3);
    });

    it("renders leftmost v-maze-card exactly at 0", async () => {
        givenVGameBoard();

        await nextTick();

        var xPos = findLowestPositionOfMazeCard(vGameBoard, "x");
        expect(xPos).toBe(0);
    });

    it("renders topmost v-maze-card exactly at 0", async () => {
        givenVGameBoard();

        await nextTick();

        var yPos = findLowestPositionOfMazeCard(vGameBoard, "y");
        expect(yPos).toBe(0);
    });
});

let vGameBoard;
let stores;

function givenVGameBoard() {
    vGameBoard = mount(VGameBoard, {
        global: {
            plugins: [createTestingPinia({ stubActions: false })],
        },
    });
    stores = createTestStores(GET_GAME_STATE_RESULT_FOR_N_3);
}
