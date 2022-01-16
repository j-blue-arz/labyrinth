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
    enterGame({ commit, getters, rootGetters, dispatch }) {
        if (!getters.hasUserPlayer) {
            if (rootGetters["game/isOnline"]) {
                API.doAddPlayer(apiPlayer => {
                    apiPlayer.isUser = true;
                    commit("addPlayer", apiPlayer);
                });
            } else {
                const playerMazeCard = rootGetters["board/mazeCard"]({ row: 0, column: 0 });
                const player = createPlayer(0);
                player.isUser = true;
                player.mazeCardId = playerMazeCard.id;
                commit("addPlayer", player);
                dispatch("game/playerWasAdded", null, { root: true });
            }
        }
    },
    leaveGame({ getters, dispatch }) {
        if (getters.hasUserPlayer) {
            dispatch("removeClientPlayer", getters.userPlayerId);
        }
    },
    addWasmPlayer({ commit, getters, rootGetters, rootState, dispatch }) {
        if (!getters.hasWasmPlayer) {
            if (rootGetters["game/isOnline"]) {
                API.doAddPlayer(apiPlayer => {
                    apiPlayer.isWasm = true;
                    commit("addPlayer", apiPlayer);
                });
            } else {
                const playerMazeCard = rootGetters["board/mazeCard"]({
                    row: 0,
                    column: rootState.board.mazeSize - 1
                });
                const player = createPlayer(1);
                player.isWasm = true;
                player.mazeCardId = playerMazeCard.id;
                commit("addPlayer", player);
                dispatch("game/playerWasAdded", null, { root: true });
            }
        }
    },
    removeWasmPlayer({ getters, dispatch }) {
        if (getters.hasWasmPlayer) {
            dispatch("removeClientPlayer", getters.wasmPlayerId);
        }
    },
    removeAllClientPlayers({ dispatch }) {
        dispatch("removeWasmPlayer");
        dispatch("leaveGame");
    },
    removeClientPlayer({ getters, dispatch, commit, rootGetters }, playerId) {
        if (getters.userPlayerId === playerId || getters.wasmPlayerId === playerId) {
            if (rootGetters["game/isOnline"]) {
                API.removePlayer(playerId);
            }
            commit("removePlayer", playerId);
            dispatch("game/playerWasRemoved", playerId, { root: true });
        }
    },
    changeUserPlayerName({ getters, commit, rootGetters }, newName) {
        if (getters.hasUserPlayer) {
            const playerId = getters.userPlayerId;
            if (rootGetters["game/isOnline"]) {
                API.changePlayerName(playerId, newName);
            }
            commit("changeName", { id: playerId, name: newName });
        }
    },
    objectiveReached({ commit }, playerId) {
        commit("increaseScore", playerId);
    }
};

export const mutations = {
    setPlayerCard(state, cardChange) {
        state.byId[cardChange.playerId].mazeCardId = cardChange.mazeCardId;
    },
    addPlayer(state, playerToAdd) {
        let defaultPlayer = newPlayer(playerToAdd.id);
        let player = fillPlayer(defaultPlayer, playerToAdd);
        Vue.set(state.byId, player.id, player);
        state.allIds.push(player.id);
    },
    removePlayer(state, id) {
        const player = state.byId[id];
        Vue.delete(state.byId, id);
        const index = state.allIds.indexOf(id);
        state.allIds.splice(index, 1);
    },
    updatePlayer(state, player) {
        let existingPlayer = state.byId[player.id];
        let updatedPlayer = fillPlayer(existingPlayer, player);
        Vue.set(state.byId, updatedPlayer.id, updatedPlayer);
    },
    changeName(state, nameChange) {
        state.byId[nameChange.id].name = nameChange.name;
    },
    increaseScore(state, playerId) {
        state.byId[playerId].score += 1;
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};

function fillPlayer(playerToFill, apiPlayer) {
    let player = { ...playerToFill, ...apiPlayer };
    return player;
}

function newPlayer(id) {
    return { id: id, name: "", score: 0 };
}

function createPlayer(playerId) {
    let player = {
        id: playerId,
        pieceIndex: playerId
    };
    return player;
}
