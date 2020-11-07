import { mount } from "@vue/test-utils";
import DraggableGameBoard from "@/components/DraggableGameBoard.vue";
import Game from "@/model/game";
import VGameBoard from "@/components/VGameBoard.vue";
import { buildRandomMaze } from "./testutils.js";

describe("DraggableGameBoard", () => {
    it("offsets position of maze card when dragging occurs", async () => {
        const wrapper = factory();
        wrapper.element.getScreenCTM = function() {
            return { e: 0, f: 0, a: 1, d: 1 };
        };
        wrapper.trigger("mousedown", { clientX: 150, clientY: 150 });
        await wrapper.trigger("mousemove", { clientX: 190, clientY: 150 });
        const drag = wrapper.find(VGameBoard).props("drag");
        expect(drag.mazeCardId).toBe(4);
        expect(drag.offset.x).toBe(40);
    });
});

const factory = function() {
    let game = new Game();
    game.n = 3;
    buildRandomMaze(game);
    return mount(DraggableGameBoard, {
        propsData: {
            game: game
        }
    });
};
