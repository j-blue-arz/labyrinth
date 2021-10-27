import API from "@/services/game-api.js";

export const state = () => ({
    nextAction: null,
    isServed: false,
    objectiveId: -1
});

const stateInitializer = state;

const getters = {
    currentPlayer: (state, _, __, rootGetters) => {
        if (state.nextAction) {
            return rootGetters["players/find"](state.nextAction.playerId);
        } else {
            return null;
        }
    }
};

const actions = {
    update({ commit, dispatch }, apiState) {
        commit("update", apiState);
        dispatch("players/update", apiState.players, { root: true });
        const boardState = {
            maze: apiState.maze,
            enabledShiftLocations: apiState.enabledShiftLocations,
            players: apiState.players
        };
        dispatch("board/update", boardState, { root: true });
    },
    reset({ commit, dispatch }) {
        commit("reset");
        dispatch("players/update", [], { root: true });
        const boardState = {
            maze: { mazeSize: 0 },
            enabledShiftLocations: [],
            players: []
        };
        dispatch("board/update", boardState, { root: true });
    },
    move({ dispatch, rootGetters }, moveAction) {
        // already validated
        const targetCard = rootGetters["board/mazeCard"](moveAction.targetLocation);
        const sourceCard = rootGetters["players/mazeCard"](moveAction.playerId);
        const boardMove = {
            sourceCardId: sourceCard.id,
            targetCardId: targetCard.id,
            playerId: moveAction.playerId
        };
        dispatch("board/movePlayer", boardMove, { root: true });

        const cardChange = { playerId: moveAction.playerId, mazeCardId: targetCard.id };
        dispatch("players/changePlayersCard", cardChange, { root: true });
        API.doMove(moveAction.playerId, moveAction.targetLocation);
    },
    shift({ dispatch, rootGetters }, shiftAction) {
        API.doShift(
            shiftAction.playerId,
            shiftAction.location,
            shiftAction.leftoverRotation,
            () => {}
        );

        const shiftLocation = shiftAction.location;
        const oppositeLocation = rootGetters["board/oppositeLocation"](shiftLocation);
        const pushedOutCard = rootGetters["board/mazeCard"](oppositeLocation);
        const pushedOutPlayerIds = [...pushedOutCard.playerIds];
        const leftoverCard = rootGetters["board/leftoverMazeCard"];
        dispatch("board/shift", shiftAction, { root: true });
        for (let playerId of pushedOutPlayerIds) {
            const cardChange = { playerId: playerId, mazeCardId: leftoverCard.id };
            dispatch("players/changePlayersCard", cardChange, { root: true });
        }
    }
};

export const mutations = {
    update(state, apiState) {
        state.objectiveId = apiState.objectiveMazeCardId;
        state.nextAction = apiState.nextAction;
        state.isServed = true;
    },
    reset(state) {
        Object.assign(state, stateInitializer());
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};
