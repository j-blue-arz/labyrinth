import DraggableGameBoard from "@/components/DraggableGameBoard.vue";
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import { MOVE_ACTION, SHIFT_ACTION } from "@/model/player.js";
import { loc } from "@/stores/board.js";
import { createTestingPinia } from "@pinia/testing";
import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { nextTick } from "vue";
import { createTestStores } from "../testfixtures.js";

describe("InteractiveBoard", () => {
    beforeEach(() => {
        givenInteractiveBoard();
        givenUserPlayer();
    });

    it("sets interaction class on reachable maze cards", async () => {
        await whenMoveRequired();

        thenCardsAreInteractive([loc(0, 2), loc(0, 3), loc(1, 2), loc(2, 2), loc(3, 2)]);
    });

    it("does not set interaction class if shift is required", async () => {
        await whenShiftRequired();

        thenCardsAreInteractive([]);
    });

    it("calls performMove() on controller when maze card is clicked", async () => {
        await givenMoveRequired();

        await whenMazeCardIsClickedAtLocation(loc(0, 2));

        thenMoveIsCalled(loc(0, 2));
    });

    it("does not call performMove() if shift is required", async () => {
        givenShiftRequired();

        await whenMazeCardIsClickedAtLocation(loc(0, 2));

        thenMoveIsNotCalled();
    });

    it("does not call performMove() if clicked maze card is not reachable", async () => {
        givenMoveRequired();

        await whenMazeCardIsClickedAtLocation(loc(0, 0));

        thenMoveIsNotCalled();
    });
});

let interactiveBoard;
let stores;

const userPlayerId = 5;

function givenUserPlayer() {
    stores.playersStore.addPlayer({ id: userPlayerId, isUser: true });
    stores.gameStore.updateFromApi(API_STATE);
}

function givenInteractiveBoard() {
    interactiveBoard = mount(InteractiveBoard, {
        global: {
            plugins: [createTestingPinia({ stubActions: false, createSpy: vi.fn })],
        },
    });
    stores = createTestStores();
}

function givenShiftRequired() {
    whenShiftRequired();
}

const whenShiftRequired = async function () {
    stores.gameStore.updateNextAction({ playerId: userPlayerId, action: SHIFT_ACTION });
    await nextTick();
};

async function givenMoveRequired() {
    await whenMoveRequired();
}

const whenMoveRequired = async function () {
    stores.gameStore.updateNextAction({ playerId: userPlayerId, action: MOVE_ACTION });
    await nextTick();
};

async function whenMazeCardIsClickedAtLocation(location) {
    const clickedMazeCard = stores.boardStore.mazeCard(location);
    await interactiveBoard
        .findComponent(DraggableGameBoard)
        .vm.$emit("player-move", clickedMazeCard);
}

function thenMoveIsCalled(toLocation) {
    expect(stores.gameStore.move).toHaveBeenCalledWith({
        playerId: userPlayerId,
        targetLocation: toLocation,
    });
}

function thenMoveIsNotCalled() {
    expect(stores.gameStore.move).not.toHaveBeenCalled();
}

function fetchInteractiveCardIds() {
    let mazeCards = interactiveBoard.findAll(".maze-card");
    let interactiveCardIds = [];
    for (var i = 0; i < mazeCards.length; i++) {
        let card = mazeCards[i];
        if (card.classes("maze-card--interactive")) {
            interactiveCardIds.push(parseInt(card.attributes("id")));
        }
    }
    return interactiveCardIds;
}

function thenCardsAreInteractive(reachableCardLocations) {
    let reachableCardIds = reachableCardLocations.map(
        (location) => stores.boardStore.mazeCard(location).id,
    );

    let interactiveCardIds = fetchInteractiveCardIds();
    expect(interactiveCardIds.length).toBe(reachableCardIds.length);
    expect(interactiveCardIds).toEqual(expect.arrayContaining(reachableCardIds));
}

/* GENERATED_WITH_LINE_LEFTOVER =
###|#.#|###|#.#|###|###|###|
#..|#.#|...|.o#|...|...|..#|
#.#|#.#|#.#|###|#.#|###|#.#|
---------------------------|
###|###|#.#|#.#|###|###|###|
..#|...|#.#|..#|..#|...|#..|
#.#|###|#.#|#.#|#.#|#.#|#.#|
---------------------------|
#.#|###|#.#|#.#|###|###|#.#|
#..|...|#..|#.#|...|...|..#|
#.#|###|#.#|#.#|#.#|###|#.#|
---------------------------|
#.#|###|#.#|#.#|###|#.#|###|
#..|..#|#..|#..|...|#.#|...|
#.#|#.#|###|###|#.#|#.#|###|
---------------------------|
#.#|###|#.#|###|#.#|###|#.#|
#..|..#|...|..#|..#|..#|..#|
#.#|#.#|###|#.#|#.#|#.#|#.#|
---------------------------|
#.#|#.#|###|#.#|###|###|###|
#..|#..|..#|#..|..#|...|...|
#.#|###|#.#|#.#|#.#|###|###|
---------------------------|
#.#|###|#.#|#.#|#.#|#.#|#.#|
#..|..#|...|#..|...|#..|..#|
###|#.#|###|###|###|#.#|###|
---------------------------* */

const API_STATE = {
    maze: {
        mazeSize: 7,
        mazeCards: [
            {
                outPaths: "NS",
                id: 49,
                location: null,
                rotation: 270,
            },
            {
                outPaths: "NE",
                id: 0,
                location: {
                    column: 0,
                    row: 0,
                },
                rotation: 90,
            },
            {
                outPaths: "NS",
                id: 1,
                location: {
                    column: 1,
                    row: 0,
                },
                rotation: 180,
            },
            {
                outPaths: "NES",
                id: 2,
                location: {
                    column: 2,
                    row: 0,
                },
                rotation: 90,
            },
            {
                outPaths: "NE",
                id: 3,
                location: {
                    column: 3,
                    row: 0,
                },
                rotation: 270,
            },
            {
                outPaths: "NES",
                id: 4,
                location: {
                    column: 4,
                    row: 0,
                },
                rotation: 90,
            },
            {
                outPaths: "NS",
                id: 5,
                location: {
                    column: 5,
                    row: 0,
                },
                rotation: 90,
            },
            {
                outPaths: "NE",
                id: 6,
                location: {
                    column: 6,
                    row: 0,
                },
                rotation: 180,
            },
            {
                outPaths: "NE",
                id: 7,
                location: {
                    column: 0,
                    row: 1,
                },
                rotation: 180,
            },
            {
                outPaths: "NS",
                id: 8,
                location: {
                    column: 1,
                    row: 1,
                },
                rotation: 90,
            },
            {
                outPaths: "NS",
                id: 9,
                location: {
                    column: 2,
                    row: 1,
                },
                rotation: 180,
            },
            {
                outPaths: "NES",
                id: 10,
                location: {
                    column: 3,
                    row: 1,
                },
                rotation: 180,
            },
            {
                outPaths: "NE",
                id: 11,
                location: {
                    column: 4,
                    row: 1,
                },
                rotation: 180,
            },
            {
                outPaths: "NES",
                id: 12,
                location: {
                    column: 5,
                    row: 1,
                },
                rotation: 90,
            },
            {
                outPaths: "NE",
                id: 13,
                location: {
                    column: 6,
                    row: 1,
                },
                rotation: 90,
            },
            {
                outPaths: "NES",
                id: 14,
                location: {
                    column: 0,
                    row: 2,
                },
                rotation: 0,
            },
            {
                outPaths: "NS",
                id: 15,
                location: {
                    column: 1,
                    row: 2,
                },
                rotation: 90,
            },
            {
                outPaths: "NES",
                id: 16,
                location: {
                    column: 2,
                    row: 2,
                },
                rotation: 0,
            },
            {
                outPaths: "NS",
                id: 17,
                location: {
                    column: 3,
                    row: 2,
                },
                rotation: 180,
            },
            {
                outPaths: "NES",
                id: 18,
                location: {
                    column: 4,
                    row: 2,
                },
                rotation: 90,
            },
            {
                outPaths: "NS",
                id: 19,
                location: {
                    column: 5,
                    row: 2,
                },
                rotation: 90,
            },
            {
                outPaths: "NES",
                id: 20,
                location: {
                    column: 6,
                    row: 2,
                },
                rotation: 180,
            },
            {
                outPaths: "NES",
                id: 21,
                location: {
                    column: 0,
                    row: 3,
                },
                rotation: 0,
            },
            {
                outPaths: "NE",
                id: 22,
                location: {
                    column: 1,
                    row: 3,
                },
                rotation: 180,
            },
            {
                outPaths: "NE",
                id: 23,
                location: {
                    column: 2,
                    row: 3,
                },
                rotation: 0,
            },
            {
                outPaths: "NE",
                id: 24,
                location: {
                    column: 3,
                    row: 3,
                },
                rotation: 0,
            },
            {
                outPaths: "NES",
                id: 25,
                location: {
                    column: 4,
                    row: 3,
                },
                rotation: 90,
            },
            {
                outPaths: "NS",
                id: 26,
                location: {
                    column: 5,
                    row: 3,
                },
                rotation: 180,
            },
            {
                outPaths: "NS",
                id: 27,
                location: {
                    column: 6,
                    row: 3,
                },
                rotation: 90,
            },
            {
                outPaths: "NES",
                id: 28,
                location: {
                    column: 0,
                    row: 4,
                },
                rotation: 0,
            },
            {
                outPaths: "NE",
                id: 29,
                location: {
                    column: 1,
                    row: 4,
                },
                rotation: 180,
            },
            {
                outPaths: "NES",
                id: 30,
                location: {
                    column: 2,
                    row: 4,
                },
                rotation: 270,
            },
            {
                outPaths: "NE",
                id: 31,
                location: {
                    column: 3,
                    row: 4,
                },
                rotation: 180,
            },
            {
                outPaths: "NES",
                id: 32,
                location: {
                    column: 4,
                    row: 4,
                },
                rotation: 180,
            },
            {
                outPaths: "NE",
                id: 33,
                location: {
                    column: 5,
                    row: 4,
                },
                rotation: 180,
            },
            {
                outPaths: "NES",
                id: 34,
                location: {
                    column: 6,
                    row: 4,
                },
                rotation: 180,
            },
            {
                outPaths: "NES",
                id: 35,
                location: {
                    column: 0,
                    row: 5,
                },
                rotation: 0,
            },
            {
                outPaths: "NE",
                id: 36,
                location: {
                    column: 1,
                    row: 5,
                },
                rotation: 0,
            },
            {
                outPaths: "NE",
                id: 37,
                location: {
                    column: 2,
                    row: 5,
                },
                rotation: 180,
            },
            {
                outPaths: "NES",
                id: 38,
                location: {
                    column: 3,
                    row: 5,
                },
                rotation: 0,
            },
            {
                outPaths: "NE",
                id: 39,
                location: {
                    column: 4,
                    row: 5,
                },
                rotation: 180,
            },
            {
                outPaths: "NS",
                id: 40,
                location: {
                    column: 5,
                    row: 5,
                },
                rotation: 90,
            },
            {
                outPaths: "NS",
                id: 41,
                location: {
                    column: 6,
                    row: 5,
                },
                rotation: 90,
            },
            {
                outPaths: "NE",
                id: 42,
                location: {
                    column: 0,
                    row: 6,
                },
                rotation: 0,
            },
            {
                outPaths: "NE",
                id: 43,
                location: {
                    column: 1,
                    row: 6,
                },
                rotation: 180,
            },
            {
                outPaths: "NES",
                id: 44,
                location: {
                    column: 2,
                    row: 6,
                },
                rotation: 270,
            },
            {
                outPaths: "NE",
                id: 45,
                location: {
                    column: 3,
                    row: 6,
                },
                rotation: 0,
            },
            {
                outPaths: "NES",
                id: 46,
                location: {
                    column: 4,
                    row: 6,
                },
                rotation: 270,
            },
            {
                outPaths: "NES",
                id: 47,
                location: {
                    column: 5,
                    row: 6,
                },
                rotation: 0,
            },
            {
                outPaths: "NE",
                id: 48,
                location: {
                    column: 6,
                    row: 6,
                },
                rotation: 270,
            },
        ],
    },
    nextAction: {
        action: "MOVE",
        playerId: 5,
    },
    objectiveMazeCardId: 34,
    players: [
        {
            id: 5,
            isBot: false,
            mazeCardId: 3,
        },
    ],
    enabledShiftLocations: [
        {
            column: 0,
            row: 3,
        },
        {
            column: 6,
            row: 5,
        },
        {
            column: 6,
            row: 1,
        },
        {
            column: 5,
            row: 0,
        },
        {
            column: 0,
            row: 1,
        },
        {
            column: 3,
            row: 0,
        },
        {
            column: 5,
            row: 6,
        },
        {
            column: 1,
            row: 0,
        },
        {
            column: 1,
            row: 6,
        },
        {
            column: 3,
            row: 6,
        },
        {
            column: 6,
            row: 3,
        },
        {
            column: 0,
            row: 5,
        },
    ],
};
