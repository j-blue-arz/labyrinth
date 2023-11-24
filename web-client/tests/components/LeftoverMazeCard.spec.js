import LeftoverMazeCard from "@/components/LeftoverMazeCard.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import * as action from "@/model/player.js";
import { createTestingPinia } from "@pinia/testing";
import { mount } from "@vue/test-utils";

import { useBoardStore } from "@/stores/board.js";
import { useGameStore } from "@/stores/game.js";
import { usePlayersStore } from "@/stores/players.js";
import { expect } from "vitest";
import { nextTick } from "vue";

describe("InteractiveBoard", () => {
    beforeEach(() => {
        givenLeftoverMazeCard();
    });

    it("rotates leftover maze card when clicked", async () => {
        givenRotation(0);
        givenShiftRequired();

        await whenMazeCardIsClicked();

        thenMazeCardWasRotated();
    });

    it("does not rotate leftover maze card given no interaction required", async () => {
        givenRotation(0);
        givenNoActionRequired();

        await whenMazeCardIsClicked();

        thenMazeCardWasNotRotated();
    });

    it("assigns class 'interaction' on leftover maze card when interaction is required", async () => {
        givenShiftRequired();
        await nextTick();

        thenMazeCardIsInteractive();
    });

    it("removes class 'interaction' on leftover maze card when no interaction required", async () => {
        givenNoActionRequired();
        await nextTick();

        thenMazeCardIsNotInteractive();
    });
});

let leftoverMazeCard;
let gameStore;
let playersStore;
let boardStore;

const mazeCard = { id: 0, location: null, outPaths: "NS", rotation: 0 };

const factory = function () {
    const testingPinia = createTestingPinia({
        game: {
            objectiveId: 1,
        },
    });
    gameStore = useGameStore();
    playersStore = usePlayersStore();
    playersStore.findByMazeCard = () => [];
    boardStore = useBoardStore();
    boardStore.leftoverMazeCard = mazeCard;
    let leftoverMazeCard = mount(LeftoverMazeCard, {
        global: {
            plugins: [testingPinia],
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
    playersStore.userPlayer = { id: 0, nextAction: action.SHIFT_ACTION };
};

const givenNoActionRequired = function () {
    playersStore.userPlayer = { id: 0, nextAction: action.NO_ACTION };
};

const whenMazeCardIsClicked = async function () {
    await leftoverMazeCard.findComponent(VMazeCard).trigger("click");
};

const thenMazeCardWasRotated = function () {
    expect(boardStore.rotateLeftoverClockwise).toHaveBeenCalledTimes(1);
};

const thenMazeCardWasNotRotated = function () {
    expect(boardStore.rotateLeftoverClockwise).toHaveBeenCalledTimes(0);
};

const thenMazeCardIsInteractive = function () {
    let leftoverVMazeCard = leftoverMazeCard.findComponent(VMazeCard);
    expect(leftoverVMazeCard.classes()).toContain("maze-card--interactive");
};

const thenMazeCardIsNotInteractive = function () {
    let leftoverVMazeCard = leftoverMazeCard.findComponent(VMazeCard);
    expect(leftoverVMazeCard.classes()).not.toContain("maze-card--interactive");
};
