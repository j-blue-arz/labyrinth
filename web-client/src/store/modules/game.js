import * as action from "@/model/player.js";

export const state = () => ({
    playerIds: [], // check if needed
    nextAction: { playerId: 0, action: action.NO_ACTION },
    isServed: false,
    objectiveId: -1
});

const getters = {};

const actions = {};

export const mutations = {
    setGameFromApi(state, apiState) {
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
