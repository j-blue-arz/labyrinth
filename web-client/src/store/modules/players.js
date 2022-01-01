import Vue from "vue";
import API from "@/services/game-api.js";
import * as action from "@/model/player.js";

export const state = () => ({
    byId: {},
    allIds: []
});

const getters = {
    find: (state, _, rootState) => id => {
        const player = state.byId[id];
        if (player) {
            const nextAction = rootState.game.nextAction;
            return {
                ...player,
                nextAction: nextAction?.playerId === id ? nextAction.action : action.NO_ACTION
            };
        } else {
            return undefined;
        }
    },
    all: (state, getters) => {
        return state.allIds.map(id => getters.find(id));
    },
    findByMazeCard: (_, getters) => cardId => {
        return getters.all.filter(player => player.mazeCardId === cardId);
    },
    mazeCard: (state, _, __, rootGetters) => id => {
        const player = state.byId[id];
        return rootGetters["board/mazeCardById"](player.mazeCardId);
    },
    hasUserPlayer: state => {
        return state.allIds.some(id => state.byId[id].isUser);
    },
    userPlayerId: state => {
        return state.allIds.find(id => state.byId[id].isUser);
    },
    userPlayer: (_, getters) => {
        return getters.find(getters.userPlayerId);
    },
    hasWasmPlayer: state => {
        return state.allIds.some(id => state.byId[id].isWasm);
    },
    wasmPlayerId: state => {
        return state.allIds.find(id => state.byId[id].isWasm);
    },
    wasmPlayer: (_, getters) => {
        return getters.find(getters.wasmPlayerId);
    },
    bots: (_, getters) => {
        return getters.all.filter(player => player.isBot);
    }
};

const actions = {
    update({ commit, state }, apiPlayers) {
        const apiIds = apiPlayers.map(apiPlayer => apiPlayer.id);
        const removedPlayerIds = state.allIds.filter(id => !apiIds.includes(id));
        removedPlayerIds.forEach(playerId => {
            commit("removePlayer", playerId);
        });
        apiPlayers.forEach(apiPlayer => {
            if (state.allIds.includes(apiPlayer.id)) {
                commit("updatePlayer", apiPlayer);
            } else {
                commit("addPlayer", apiPlayer);
            }
        });
    },
    changePlayersCard({ commit }, cardChange) {
        commit("setPlayerCard", cardChange);
    },
    enterGame({ commit, getters }) {
        if (!getters.hasUserPlayer) {
            API.doAddPlayer(apiPlayer => {
                apiPlayer.isUser = true;
                commit("addPlayer", apiPlayer);
            });
        }
    },
    leaveGame({ commit, getters }) {
        if (getters.hasUserPlayer) {
            const playerId = getters.userPlayerId;
            API.removePlayer(playerId);
            commit("removePlayer", playerId);
        }
    },
    addWasmPlayer({ commit, getters }) {
        if (!getters.hasWasmPlayer) {
            API.doAddPlayer(apiPlayer => {
                apiPlayer.isWasm = true;
                commit("addPlayer", apiPlayer);
            });
        }
    },
    removeWasmPlayer({ commit, getters }) {
        if (getters.hasWasmPlayer) {
            const playerId = getters.wasmPlayerId;
            API.removePlayer(playerId);
            commit("removePlayer", playerId);
        }
    },
    removeAllClientPlayers({ dispatch }) {
        dispatch("removeWasmPlayer");
        dispatch("leaveGame");
    },
    removeClientPlayer({ getters, dispatch }, playerId) {
        if (getters.userPlayerId === playerId) {
            dispatch("leaveGame");
        } else if (getters.wasmPlayerId === playerId) {
            dispatch("removeWasmPlayer");
        }
    },
    changeUserPlayerName({ getters, commit }, newName) {
        if (getters.hasUserPlayer) {
            const playerId = getters.userPlayerId;
            API.changePlayerName(playerId, newName);
            commit("changeName", { id: playerId, name: newName });
        }
    }
};

export const mutations = {
    setPlayerCard(state, cardChange) {
        state.byId[cardChange.playerId].mazeCardId = cardChange.mazeCardId;
    },
    addPlayer(state, apiPlayer) {
        let player = newPlayer(apiPlayer.id);
        player = fillFromApi(player, apiPlayer);
        Vue.set(state.byId, player.id, player);
        state.allIds.push(player.id);
    },
    removePlayer(state, id) {
        const player = state.byId[id];
        Vue.delete(state.byId, id);
        const index = state.allIds.indexOf(id);
        state.allIds.splice(index, 1);
    },
    updatePlayer(state, apiPlayer) {
        let player = state.byId[apiPlayer.id];
        player = fillFromApi(player, apiPlayer);
        Vue.set(state.byId, player.id, player);
    },
    changeName(state, nameChange) {
        state.byId[nameChange.id].name = nameChange.name;
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};

function fillFromApi(playerToFill, apiPlayer) {
    let player = { ...playerToFill, ...apiPlayer };
    return player;
}

function newPlayer(id) {
    return { id: id, name: "" };
}
