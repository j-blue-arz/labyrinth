import { mount } from "@vue/test-utils";
import DraggableGameBoard from "@/components/DraggableGameBoard.vue";
import Game, { loc } from "@/model/game.js";
import VGameBoard from "@/components/VGameBoard.vue";
import { buildRandomMaze } from "./testutils.js";

beforeEach(() => {
    wrapper = factory();
    game = wrapper.props("game");
});

describe("DraggableGameBoard", () => {
    it("offsets position of maze card when dragging occurs", () => {
        givenMouseDownAt(loc(1, 1));

        whenMouseIsMoved({ x: 40, y: 0 });

        thenDraggedMazeCardAtLocation(loc(1, 1));
        thenMazeCardIsDragged({ x: 40, y: 0 });
    });
});

let wrapper = null;
let game = null;
let mousePosition = null;

const factory = function() {
    let game = new Game();
    game.n = 3;
    buildRandomMaze(game);
    let wrapper = mount(DraggableGameBoard, {
        propsData: {
            game: game
        }
    });
    wrapper.element.getScreenCTM = function() {
        return { e: 0, f: 0, a: 1, d: 1 };
    };
    return wrapper;
};

const givenMouseDownAt = function(location) {
    const clientX = location.column * 100 + 50;
    const clientY = location.row * 100 + 50;
    mousePosition = { clientX: clientX, clientY: clientY };
    wrapper.trigger("mousedown", mousePosition);
};

const whenMouseIsMoved = function(offset) {
    const clientX = mousePosition.clientX + offset.x;
    const clientY = mousePosition.clientY + offset.y;
    mousePosition = { clientX: clientX, clientY: clientY };
    wrapper.trigger("mousemove", mousePosition);
};

const thenDraggedMazeCardAtLocation = function(expectedLocation) {
    const drag = wrapper.find(VGameBoard).props("drag");
    const expectedId = game.getMazeCard(expectedLocation).id;
    expect(drag.mazeCardId).toBe(expectedId);
};

const thenMazeCardIsDragged = function(expectedOffset) {
    const drag = wrapper.find(VGameBoard).props("drag");
    expect(drag.offset.x).toBe(expectedOffset.x);
    expect(drag.offset.y).toBe(expectedOffset.y);
};
