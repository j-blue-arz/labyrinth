import * as action from "@/model/player.js";
import API from "@/services/game-api.js";

export const state = () => ({
    playerIds: [],
    nextAction: { playerId: 0, action: action.NO_ACTION },
    isServed: false,
    objectiveId: -1
});

const getters = {};

const actions = {
    async updateFromApi({ commit, dispatch }) {
        const apiResult = await API.fetchState();
        const apiState = apiResult.data;
        commit("update", apiState);
        dispatch("players/update", apiState.players, { root: true });
        const boardState = {
            maze: apiState.maze,
            enabledShiftLocations: apiState.enabledShiftLocations,
            players: apiState.players
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
    },
    shift({ dispatch, rootGetters }, shiftLocation) {
        const oppositeLocation = rootGetters["board/oppositeLocation"](shiftLocation);
        const pushedOutCard = rootGetters["board/mazeCard"](oppositeLocation);
        const pushedOutPlayerIds = [...pushedOutCard.playerIds];
        const leftoverCard = rootGetters["board/leftoverMazeCard"];
        dispatch("board/shift", shiftLocation, { root: true });
        for (let playerId of pushedOutPlayerIds) {
            const cardChange = { playerId: playerId, mazeCardId: leftoverCard.id };
            dispatch("players/changePlayersCard", cardChange, { root: true });
        }
    }
};

export const mutations = {
    update(state, apiState) {
        state.playerIds = apiState.players.map(player => player.id);
        state.objectiveId = apiState.objectiveMazeCardId;
        if (apiState.nextAction !== null) {
            state.nextAction = apiState.nextAction;
        } else {
            state.nextAction = { playerId: 0, action: action.NO_ACTION };
        }
        state.isServed = true;
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};
