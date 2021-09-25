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
        const apiResult = await API.fetchState();
        const apiState = apiResult.data;
        commit("update", apiState);
        commit("players/update", apiState.players, { root: true });
        const boardState = {
            maze: apiState.maze,
            enabledShiftLocations: apiState.enabledShiftLocations,
            players: apiState.players
        };
        commit("board/update", boardState, { root: true });
    },
    move({ commit, rootGetters }, moveAction) {
        // already validated, so we can alter the game state directly
        const targetCard = rootGetters["board/mazeCard"](moveAction.targetLocation);
        const sourceCard = rootGetters["players/mazeCard"](moveAction.playerId);
        const boardMove = {
            sourceCardId: sourceCard.id,
            targetCardId: targetCard.id,
            playerId: moveAction.playerId
        };
        commit("board/move", boardMove, { root: true });

        const playerMove = { playerId: moveAction.playerId, mazeCardId: targetCard.id };
        commit("players/move", playerMove, { root: true });
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
