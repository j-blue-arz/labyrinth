import { createTestStore } from "../testfixtures.js";
import { mount } from "@vue/test-utils";
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import DraggableGameBoard from "@/components/DraggableGameBoard.vue";
import { SHIFT_ACTION, MOVE_ACTION } from "@/model/player.js";
import { loc } from "@/store/modules/board.js";
import { nextTick } from "vue";

describe("InteractiveBoard", () => {
    beforeEach(() => {
        givenInteractiveBoard();
        givenUserPlayer();
        store.dispatch = jest.fn();
    });

    it("sets interaction class on reachable maze cards", async () => {
        await whenMoveRequired();

        thenCardsAreInteractive([loc(0, 2), loc(0, 3), loc(1, 2), loc(2, 2), loc(3, 2)]);
    });

    it("does not set interaction class if shift is required", async () => {
        await whenShiftRequired();

        thenCardsAreInteractive([]);
    });

    it("calls performMove() on controller when maze card is clicked", () => {
        givenMoveRequired();

        whenMazeCardIsClickedAtLocation(loc(0, 2));

        thenMoveIsDispatched(loc(0, 2));
    });

    it("does not call performMove() if shift is required", () => {
        givenShiftRequired();

        whenMazeCardIsClickedAtLocation(loc(0, 2));

        thenMoveIsNotDispatched();
    });

    it("does not call performMove() if clicked maze card is not reachable", () => {
        givenMoveRequired();

        whenMazeCardIsClickedAtLocation(loc(0, 0));

        thenMoveIsNotDispatched();
    });
});

let interactiveBoard;
let store;

const userPlayerId = 5;

function givenUserPlayer() {
    store.commit("players/addPlayer", { id: userPlayerId, isUser: true });
    store.dispatch("game/updateFromApi", API_STATE);
}

function givenInteractiveBoard() {
    store = createTestStore();
    interactiveBoard = mount(InteractiveBoard, {
        global: {
            plugins: [store],
        },
    });
}

function givenShiftRequired() {
    whenShiftRequired();
}

const whenShiftRequired = async function () {
    store.commit("game/updateNextAction", { playerId: userPlayerId, action: SHIFT_ACTION });
    await nextTick();
};

function givenMoveRequired() {
    whenMoveRequired();
}

const whenMoveRequired = async function () {
    store.commit("game/updateNextAction", { playerId: userPlayerId, action: MOVE_ACTION });
    await nextTick();
};

async function whenMazeCardIsClickedAtLocation(location) {
    const clickedMazeCard = store.getters["board/mazeCard"](location);
    await interactiveBoard
        .findComponent(DraggableGameBoard)
        .vm.$emit("player-move", clickedMazeCard);
}

function thenMoveIsDispatched(toLocation) {
    expect(store.dispatch).toHaveBeenCalledWith("game/move", {
        playerId: userPlayerId,
        targetLocation: toLocation,
    });
}

function thenMoveIsNotDispatched() {
    expect(store.dispatch).not.toHaveBeenCalled();
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
        (location) => store.getters["board/mazeCard"](location).id
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
