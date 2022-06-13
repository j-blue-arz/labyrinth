import { createStore } from "vuex";
import { cloneDeep } from "lodash";

import gameConfig from "@/store/modules/game.js";
import boardConfig from "@/store/modules/board.js";
import playersConfig from "@/store/modules/players.js";

export const createTestStore = function (apiState) {
    let store = createStore({
        modules: {
            game: cloneDeep(gameConfig),
            board: cloneDeep(boardConfig),
            players: cloneDeep(playersConfig),
        },
    });
    if (apiState) {
        store.dispatch("game/updateFromApi", cloneDeep(apiState));
    }
    return store;
};

export const GET_GAME_STATE_RESULT_FOR_N_3 = {
    maze: {
        mazeSize: 3,
        mazeCards: [
            {
                outPaths: "NES",
                id: 9,
                location: null,
                rotation: 90,
            },
            {
                outPaths: "NES",
                id: 0,
                location: {
                    column: 0,
                    row: 0,
                },
                rotation: 180,
            },
            {
                outPaths: "NE",
                id: 1,
                location: {
                    column: 1,
                    row: 0,
                },
                rotation: 180,
            },
            {
                outPaths: "NS",
                id: 2,
                location: {
                    column: 2,
                    row: 0,
                },
                rotation: 90,
            },
            {
                outPaths: "NES",
                id: 3,
                location: {
                    column: 0,
                    row: 1,
                },
                rotation: 180,
            },
            {
                outPaths: "NE",
                id: 4,
                location: {
                    column: 1,
                    row: 1,
                },
                rotation: 270,
            },
            {
                outPaths: "NS",
                id: 5,
                location: {
                    column: 2,
                    row: 1,
                },
                rotation: 0,
            },
            {
                outPaths: "NS",
                id: 6,
                location: {
                    column: 0,
                    row: 2,
                },
                rotation: 180,
            },
            {
                outPaths: "NES",
                id: 7,
                location: {
                    column: 1,
                    row: 2,
                },
                rotation: 180,
            },
            {
                outPaths: "NE",
                id: 8,
                location: {
                    column: 2,
                    row: 2,
                },
                rotation: 0,
            },
        ],
    },
    players: [
        {
            id: 42,
            mazeCardId: 5,
            pieceIndex: 0,
        },
        {
            id: 17,
            pieceIndex: 1,
            mazeCardId: 5,
        },
    ],
    objectiveMazeCardId: 8,
    enabledShiftLocations: [
        { column: 1, row: 0 },
        { column: 0, row: 1 },
        { column: 2, row: 1 },
    ],
    nextAction: {
        action: "SHIFT",
        playerId: 17,
        remainingSeconds: 13,
    },
};
