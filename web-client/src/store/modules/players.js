import Vue from "vue";

export const state = () => ({
    byId: {},
    allIds: []
});

const getters = {};

const actions = {};

export const mutations = {
    setPlayersFromApi(state, apiPlayers) {
        const apiIds = apiPlayers.map(apiPlayer => apiPlayer.id);
        const removedPlayerIds = state.allIds.filter(id => !apiIds.includes(id));
        removedPlayerIds.forEach(id => Vue.delete(state.byId, id));
        apiPlayers.forEach(apiPlayer => {
            let player;
            if (state.allIds.includes(apiPlayer.id)) {
                player = state.byId[apiPlayer.id];
            } else {
                player = { id: apiPlayer.id, isUser: false, isBot: false, name: "" };
            }
            player = { ...player, ...apiPlayer };
            Vue.set(state.byId, player.id, player);
        });
        state.allIds = apiIds;
        state.allIds.sort();
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};
