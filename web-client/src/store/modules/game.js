import API from "@/services/game-api.js";
import generateBoard from "@/model/board-factory.js";
import { getShiftLocations } from "@/store/modules/board.js";
import * as action from "@/model/player.js";

const OFFLINE = "offline";
const ONLINE = "online";

export const state = () => ({
    nextAction: null,
    objectiveId: -1,
    mode: OFFLINE,
    computationMethods: [],
    turnProgressionTimeout: 0,
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
    isOffline: (state) => {
        return state.mode === OFFLINE;
    },
    isOnline: (state) => {
        return state.mode === ONLINE;
    },
    computationMethods: (state, _, __, rootGetters) => {
        if (state.mode === ONLINE) {
            return state.computationMethods;
        } else {
            if (rootGetters["players/hasWasmPlayer"]) {
                return [];
            } else {
                return ["wasm"];
            }
        }
    },
};

const actions = {
    leaveOnlineGame({ commit, dispatch, getters }) {
        if (getters.isOnline) {
            API.resetHandlers();
            API.stopPolling();
            dispatch("players/removeAllClientPlayers", null, { root: true });
            commit("offline");
        }
    },
    playOnline({ commit, dispatch, state }) {
        API.errorHandler = (error) => handleError(error);
        API.stateObserver = (apiState) => dispatch("game/updateFromApi", apiState, { root: true });
        API.activatePolling();
        commit("online");
        dispatch("players/update", [], { root: true });
        if (state.computationMethods.length === 0) {
            API.fetchComputationMethods((responseList) => {
                commit("setComputationMethods", responseList);
            });
        }
        dispatch("players/enterGame", null, { root: true });
    },
    playOffline({ commit, dispatch, rootGetters }, size = 7) {
        dispatch("leaveOnlineGame");
        commit("reset");
        dispatch("players/update", [], { root: true });

        const board = generateBoard(size);
        const boardState = {
            maze: board,
            enabledShiftLocations: getShiftLocations(size),
            players: [],
        };
        dispatch("board/update", boardState, { root: true });
        dispatch("players/enterGame", null, { root: true });
        dispatch("board/updatePlayers", rootGetters["players/all"], { root: true });

        const objectiveMazeCardId = chooseRandomObjective(rootGetters);
        commit("updateObjective", objectiveMazeCardId);
    },
    updateFromApi({ commit, dispatch }, newState) {
        commit("updateObjective", newState.objectiveMazeCardId);
        commit("updateNextAction", newState.nextAction);
        dispatch("players/update", newState.players, { root: true });
        const boardState = {
            maze: newState.maze,
            enabledShiftLocations: newState.enabledShiftLocations,
            players: newState.players,
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
            playerId: moveAction.playerId,
        };
        dispatch("board/movePlayer", boardMove, { root: true });

        const cardChange = { playerId: moveAction.playerId, mazeCardId: targetCard.id };
        dispatch("players/changePlayersCard", cardChange, { root: true });
        if (getters.isOnline) {
            API.doMove(moveAction.playerId, moveAction.targetLocation);
        } else {
            if (targetCard.id === state.objectiveId) {
                dispatch("players/objectiveReached", moveAction.playerId, { root: true });
                const objectiveMazeCardId = chooseRandomObjective(rootGetters);
                commit("updateObjective", objectiveMazeCardId);
            }
            const allPlayers = rootGetters["players/all"];
            const currentPlayerId = state.nextAction.playerId;
            const currentIndex = allPlayers.findIndex((player) => player.id === currentPlayerId);
            const nextPlayerId = allPlayers[(currentIndex + 1) % allPlayers.length].id;
            dispatch("continueTurnProgression", {
                playerId: nextPlayerId,
                action: action.SHIFT_ACTION,
            });
        }
    },
    shift({ dispatch, rootGetters, getters, state }, shiftAction) {
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
            dispatch("continueTurnProgression", {
                playerId: state.nextAction.playerId,
                action: action.MOVE_ACTION,
            });
        }
    },
    playerWasRemoved({ state, rootGetters, getters, dispatch }, playerId) {
        if (getters.isOffline) {
            if (state.nextAction.playerId === playerId) {
                const allPlayers = rootGetters["players/all"];
                if (allPlayers.length > 0) {
                    /* In offline mode, there are at maximum two players (user and wasm). Hence,
                       it is ok to pick player with index 0 here */
                    dispatch("continueTurnProgression", {
                        playerId: allPlayers[0].id,
                        action: action.SHIFT_ACTION,
                    });
                } else {
                    dispatch("abortTurnProgression");
                }
            }
        }
    },
    playerWasAdded({ rootGetters, getters, dispatch }) {
        if (getters.isOffline) {
            const allPlayers = rootGetters["players/all"];
            if (allPlayers.length == 1) {
                dispatch("continueTurnProgression", {
                    playerId: allPlayers[0].id,
                    action: action.SHIFT_ACTION,
                });
            }
        }
    },
    continueTurnProgression({ state, commit }, nextPlayerAction) {
        if (state.turnProgressionTimeout > 0) {
            clearTimeout(state.turnProgressionTimeout);
            commit("turnProgressionTimeout", 0);
        }
        const prepareAction = {
            playerId: nextPlayerAction.playerId,
            action: action.PREPARE_PREFIX + nextPlayerAction.action,
        };
        commit("updateNextAction", prepareAction);
        const timeout = setTimeout(() => commit("updateNextAction", nextPlayerAction), 800);
        commit("turnProgressionTimeout", timeout);
    },
    abortTurnProgression({ commit, state }) {
        if (state.turnProgressionTimeout > 0) {
            clearTimeout(state.turnProgressionTimeout);
            commit("turnProgressionTimeout", 0);
        }
        commit("updateNextAction", null);
    },
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
    },
    setComputationMethods(state, computationMethods) {
        state.computationMethods = computationMethods;
    },
    turnProgressionTimeout(identifier) {
        state.turnProgressionTimeout = identifier;
    },
};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations,
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

function chooseRandomObjective(rootGetters) {
    const mazeCardIds = rootGetters["board/allIds"];
    const playerCardIds = rootGetters["players/all"].map((player) => player.mazeCardId);
    let objectiveMazeCardId;
    do {
        objectiveMazeCardId = randomChoice(mazeCardIds);
    } while (playerCardIds.includes(objectiveMazeCardId));
    return objectiveMazeCardId;
}

function randomChoice(array) {
    return array[Math.floor(Math.random() * array.length)];
}
