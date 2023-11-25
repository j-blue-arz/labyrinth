import VGameBoard from "@/components/VGameBoard.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import { createTestingPinia } from "@pinia/testing";
import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";
import { nextTick } from "vue";
import { createTestStores, GET_GAME_STATE_RESULT_FOR_N_3 } from "../testfixtures.js";

const findLowestPositionOfMazeCard = function (vGameBoard, dimension) {
    const vMazeCards = vGameBoard.findAllComponents(VMazeCard);
    let min = Number.MAX_VALUE;
    for (let i = 0; i < vMazeCards.length; i++) {
        const value = parseInt(vMazeCards.at(i).element.getAttribute(dimension));
        if (value < min) {
            min = value;
        }
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

        const xPos = findLowestPositionOfMazeCard(vGameBoard, "x");
        expect(xPos).toBe(0);
    });

    it("renders topmost v-maze-card exactly at 0", async () => {
        givenVGameBoard();

        await nextTick();

        const yPos = findLowestPositionOfMazeCard(vGameBoard, "y");
        expect(yPos).toBe(0);
    });
});

let vGameBoard;

function givenVGameBoard() {
    vGameBoard = mount(VGameBoard, {
        global: {
            plugins: [createTestingPinia({ stubActions: false, createSpy: vi.fn })],
        },
    });
    createTestStores(GET_GAME_STATE_RESULT_FOR_N_3);
}
