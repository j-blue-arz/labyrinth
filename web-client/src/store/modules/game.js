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
    async updateFromApi({ commit }) {
        const apiState = await API.fetchState;
        commit("update", apiState);
        commit("players/update", apiState.players, { root: true });
        const boardState = {
            mazeSize: apiState.mazeSize,
            mazeCards: apiState.mazeCards,
            enabledShiftLocations: apiState.enabledShiftLocations,
            players: apiState.players
        };
        commit("board/update", boardState, { root: true });
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
