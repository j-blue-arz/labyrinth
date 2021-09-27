import Vue from "vue";

export const state = () => ({
    byId: {},
    allIds: []
});

const getters = {
    find: state => id => {
        return state.byId[id];
    },
    mazeCard: (state, _, __, rootGetters) => id => {
        const player = state.byId[id];
        return rootGetters["board/mazeCardById"](player.mazeCard);
    }
};

const actions = {
    update({ commit }, apiPlayers) {
        commit("update", apiPlayers);
    },
    changePlayersCard({ commit }, cardChange) {
        commit("setPlayerCard", cardChange);
    }
};

export const mutations = {
    update(state, apiPlayers) {
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
            Object.assign(player, { mazeCard: player["mazeCardId"] });
            delete player["mazeCardId"];
            Vue.set(state.byId, player.id, player);
        });
        state.allIds = apiIds;
    },
    setPlayerCard(state, cardChange) {
        state.byId[cardChange.playerId].mazeCard = cardChange.mazeCardId;
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};
