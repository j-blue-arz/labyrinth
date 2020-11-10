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
    describe("when dragging", () => {
        it("offsets entire row when dragging right", () => {
            givenMouseDownAt(loc(1, 1));

            whenMouseIsMoved({ x: 40, y: 0 });

            thenRowIsDragged(1);
            thenDragOffsetIs(40);
        });

        it("offset entire column when dragging upwards", () => {
            givenMouseDownAt(loc(1, 1));

            whenMouseIsMoved({ x: 0, y: -30 });

            thenColumnIsDragged(1);
            thenDragOffsetIs(-30);
        });

        it("drags column when dragging more down than right", () => {
            givenMouseDownAt(loc(1, 1));

            whenMouseIsMoved({ x: 20, y: 40 });

            thenColumnIsDragged(1);
            thenDragOffsetIs(40);
        });

        it("drags row when dragging more left than downwards", () => {
            givenMouseDownAt(loc(1, 1));

            whenMouseIsMoved({ x: -40, y: -20 });

            thenRowIsDragged(1);
            thenDragOffsetIs(-40);
        });

        it("drags row when dragging equally horizontally and vertically", () => {
            givenMouseDownAt(loc(1, 1));

            whenMouseIsMoved({ x: 30, y: 30 });

            thenRowIsDragged(1);
            thenDragOffsetIs(30);
        });

        it("does not offset by more than 100", () => {
            givenMouseDownAt(loc(1, 1));

            whenMouseIsMoved({ x: 120, y: 0 });

            thenRowIsDragged(1);
            thenDragOffsetIs(100);
        });
    });

    describe("does not allow dragging", () => {
        it("horizontally for not shiftable rows", () => {
            givenMouseDownAt(loc(0, 1));

            whenMouseIsMoved({ x: 40, y: 0 });

            thenNoDraggingOccurs();
        });

        it("when it is not player's turn to shift", () => {
            givenShiftIsNotRequired();
            givenMouseDownAt(loc(1, 1));

            whenMouseIsMoved({ x: 40, y: 0 });

            thenNoDraggingOccurs();
        });

        it("against the direction of the previous shift", () => {
            givenDisabledShiftLocation(loc(1, 0));
            givenMouseDownAt(loc(1, 1));

            whenMouseIsMoved({ x: 40, y: 0 });

            thenNoDraggingOccurs();
        });

        it("vertically for not shiftable columns", () => {
            givenMouseDownAt(loc(1, 0));

            whenMouseIsMoved({ x: 0, y: 30 });

            thenNoDraggingOccurs();
        });

        it("for fixed positions", () => {
            givenMouseDownAt(loc(0, 0));

            whenMouseIsMoved({ x: 40, y: 0 });

            thenNoDraggingOccurs();
        });
    });

    describe("when mouse is released", () => {
        it("emits shift event when dragged by more than 50", () => {
            givenMouseDownAt(loc(1, 1));
            givenMouseIsMoved({ x: 0, y: 75 });

            whenMouseIsReleased();

            thenNoDraggingOccurs();
            thenShiftEventIsEmitted(loc(0, 1));
        });

        it("does not emit shift event when dragged by less than 50", () => {
            givenMouseDownAt(loc(1, 1));
            givenMouseIsMoved({ x: 0, y: 25 });

            whenMouseIsReleased();

            thenNoDraggingOccurs();
            thenNoShiftEventIsEmitted();
        });
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
            userHasToShift: true,
            game: game
        }
    });
    wrapper.element.getScreenCTM = function() {
        return { e: 0, f: 0, a: 1, d: 1 };
    };
    return wrapper;
};

const givenShiftIsNotRequired = function() {
    wrapper.setProps({ userHasToShift: false });
};

const givenDisabledShiftLocation = function(location) {
    game.disabledShiftLocation = location;
};

const givenMouseDownAt = function(location) {
    const clientX = location.column * 100 + 50;
    const clientY = location.row * 100 + 50;
    mousePosition = { clientX: clientX, clientY: clientY };
    wrapper.trigger("mousedown", mousePosition);
};

const givenMouseIsMoved = function(offset) {
    whenMouseIsMoved(offset);
};

const whenMouseIsMoved = function(offset) {
    const clientX = mousePosition.clientX + offset.x;
    const clientY = mousePosition.clientY + offset.y;
    mousePosition = { clientX: clientX, clientY: clientY };
    wrapper.trigger("mousemove", mousePosition);
};

const whenMouseIsReleased = function() {
    wrapper.trigger("mouseup");
};

const thenRowIsDragged = function(expectedRow) {
    const drag = wrapper.find(VGameBoard).props("drag");
    expect(drag.row).toBe(expectedRow);
    expect([0, 1, 2]).not.toContain(drag.column);
};

const thenColumnIsDragged = function(expectedColumn) {
    const drag = wrapper.find(VGameBoard).props("drag");
    expect([0, 1, 2]).not.toContain(drag.row);
    expect(drag.column).toBe(expectedColumn);
};

const thenDragOffsetIs = function(expectedOffset) {
    const drag = wrapper.find(VGameBoard).props("drag");
    expect(drag.offset).toBe(expectedOffset);
};

const thenNoDraggingOccurs = function() {
    const drag = wrapper.find(VGameBoard).props("drag");
    expect(drag.offset).toBe(0);
};

const thenShiftEventIsEmitted = function(expectedShiftLocation) {
    expect(wrapper.emitted("player-shift")).toBeTruthy();
    expect(wrapper.emitted("player-shift").length).toBe(1);
    expect(wrapper.emitted("player-shift")[0][0].row).toBe(expectedShiftLocation.row);
    expect(wrapper.emitted("player-shift")[0][0].column).toBe(expectedShiftLocation.column);
};

const thenNoShiftEventIsEmitted = function() {
    expect(wrapper.emitted("player-shift")).toBeFalsy();
};
