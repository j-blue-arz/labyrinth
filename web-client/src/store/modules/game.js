import API from "@/services/game-api.js";
import generateBoard from "@/model/board-factory.js";
import { getShiftLocations } from "@/store/modules/board.js";
import * as action from "@/model/player.js";

const OFFLINE = "offline";
const ONLINE = "online";

export const state = () => ({
    nextAction: null,
    objectiveId: -1,
    mode: OFFLINE
});

const stateInitializer = state;

const getters = {
    currentPlayer: (state, _, __, rootGetters) => {
        if (state.nextAction) {
            return rootGetters["players/find"](state.nextAction.playerId);
        } else {
            return null;
        }
    },
    isOffline: state => {
        return state.mode === OFFLINE;
    },
    isOnline: state => {
        return state.mode === ONLINE;
    }
};

const actions = {
    enterOnlineGame({ dispatch }) {
        API.errorHandlers.push(error => handleError(error));
        API.stateObservers.push(apiState => dispatch("game/update", apiState, { root: true }));
        API.activatePolling();
        dispatch("players/enterGame", null, { root: true });
    },
    leaveOnlineGame({ commit, dispatch, getters }) {
        if (getters.isOnline) {
            API.stopPolling();
            dispatch("players/removeAllClientPlayers", null, { root: true });
        }
        commit("offline");
    },
    playOnline({ commit }) {
        commit("online");
    },
    playOffline({ commit, dispatch }) {
        dispatch("leaveOnlineGame");
        commit("reset");
        dispatch("players/update", [], { root: true });

        const board = generateBoard(7);
        const player = createPlayer(board.mazeCards[1]);
        const objectiveMazeCardId = chooseRandomObjective(board.mazeCards, player);

        const generatedState = {
            maze: board,
            enabledShiftLocations: getShiftLocations(7),
            players: [player],
            objectiveMazeCardId: objectiveMazeCardId,
            nextAction: { playerId: player.id, action: action.SHIFT_ACTION }
        };
        dispatch("update", generatedState);
    },
    update({ commit, dispatch }, newState) {
        commit("updateObjective", newState.objectiveMazeCardId);
        commit("updateNextAction", newState.nextAction);
        dispatch("players/update", newState.players, { root: true });
        const boardState = {
            maze: newState.maze,
            enabledShiftLocations: newState.enabledShiftLocations,
            players: newState.players
        };
        dispatch("board/update", boardState, { root: true });
    },
    move({ dispatch, rootGetters, getters, commit, state }, moveAction) {
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
        if (getters.isOnline) {
            API.doMove(moveAction.playerId, moveAction.targetLocation);
        } else {
            commit("updateNextAction", {
                playerId: state.nextAction.playerId,
                action: action.SHIFT_ACTION
            });
        }
    },
    shift({ dispatch, rootGetters, getters, commit, state }, shiftAction) {
        if (getters.isOnline) {
            API.doShift(
                shiftAction.playerId,
                shiftAction.location,
                shiftAction.leftoverRotation,
                () => {}
            );
        }

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

        if (getters.isOffline) {
            commit("updateNextAction", {
                playerId: state.nextAction.playerId,
                action: action.MOVE_ACTION
            });
        }
    }
};

export const mutations = {
    updateObjective(state, newObjectiveId) {
        state.objectiveId = newObjectiveId;
    },
    updateNextAction(state, newAction) {
        state.nextAction = newAction;
    },
    reset(state) {
        Object.assign(state, stateInitializer());
    },
    offline(state) {
        state.mode = OFFLINE;
    },
    online(state) {
        state.mode = ONLINE;
    }
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};

function handleError(error) {
    if (error.response) {
        if (error.response.data.key === "GAME_NOT_FOUND") {
            console.log("Game not found, resetting.");
            this.$store.dispatch("game/playOffline");
        } else {
            console.error("Response error", error.response.data);
        }
    } else if (error.request) {
        API.stopPolling();
        console.error("Request error", error.request);
    } else {
        console.error("Error", error.message);
    }
}

function createPlayer(playerMazeCard) {
    const playerId = 0;

    let player = {
        id: playerId,
        mazeCardId: playerMazeCard.id,
        pieceIndex: 0,
        isUser: true
    };
    return player;
}

function chooseRandomObjective(mazeCards, player) {
    let objectiveMazeCardId;
    do {
        objectiveMazeCardId = randomChoice(mazeCards).id;
    } while (player.mazeCardId === objectiveMazeCardId);
    return objectiveMazeCardId;
}

function randomChoice(array) {
    return array[Math.floor(Math.random() * array.length)];
}
