import { mount } from "@vue/test-utils";
import LeftoverMazeCard from "@/components/LeftoverMazeCard.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import * as action from "@/model/player.js";

describe("InteractiveBoard", () => {
    beforeEach(() => {
        mockStore = createMockStore();
    });

    it("rotates leftover maze card when clicked", () => {
        givenRotation(0);
        givenShiftRequired();
        givenLeftoverMazeCard();

        whenMazeCardIsClicked();

        thenMazeCardWasRotated();
    });

    it("does not rotate leftover maze card given no interaction required", () => {
        givenRotation(0);
        givenNoActionRequired();
        givenLeftoverMazeCard();

        whenMazeCardIsClicked();

        thenMazeCardWasNotRotated();
    });

    it("assigns class 'interaction' on leftover maze card when interaction is required", () => {
        givenShiftRequired();
        givenLeftoverMazeCard();

        thenMazeCardIsInteractive();
    });

    it("removes class 'interaction' on leftover maze card when no interaction required", () => {
        givenNoActionRequired();
        givenLeftoverMazeCard();

        thenMazeCardIsNotInteractive();
    });
});

let leftoverMazeCard;
let mockStore;

const mazeCard = { id: 0, location: null, outPaths: "NS", rotation: 0 };

const createMockStore = function () {
    return {
        getters: { "board/leftoverMazeCard": mazeCard, "players/findByMazeCard": () => [] },
        dispatch: jest.fn(),
        state: {
            game: {
                objectiveId: 1,
            },
        },
    };
};

const factory = function () {
    let leftoverMazeCard = mount(LeftoverMazeCard, {
        mocks: {
            $store: mockStore,
        },
    });
    return leftoverMazeCard;
};

const givenLeftoverMazeCard = function () {
    leftoverMazeCard = factory();
};

const givenRotation = function (rotation) {
    mazeCard.rotation = rotation;
};

const givenShiftRequired = function () {
    mockStore.getters["players/userPlayer"] = { id: 0, nextAction: action.SHIFT_ACTION };
};

const givenNoActionRequired = function () {
    mockStore.getters["players/userPlayer"] = { id: 0, nextAction: action.NO_ACTION };
};

const whenMazeCardIsClicked = function () {
    leftoverMazeCard.find(VMazeCard).trigger("click");
};

const thenMazeCardWasRotated = function () {
    expect(mockStore.dispatch).toHaveBeenCalledTimes(1);
    expect(mockStore.dispatch).toHaveBeenCalledWith("board/rotateLeftoverClockwise");
};

const thenMazeCardWasNotRotated = function () {
    expect(mockStore.dispatch).toHaveBeenCalledTimes(0);
};

const thenMazeCardIsInteractive = function () {
    let leftoverVMazeCard = leftoverMazeCard.find(VMazeCard);
    expect(leftoverVMazeCard.classes()).toContain("maze-card--interactive");
};

const thenMazeCardIsNotInteractive = function () {
    let leftoverVMazeCard = leftoverMazeCard.find(VMazeCard);
    expect(leftoverVMazeCard.classes()).not.toContain("maze-card--interactive");
};
