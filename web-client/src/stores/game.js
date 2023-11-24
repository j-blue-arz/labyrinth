import { defineStore } from "pinia";

import generateBoard from "@/model/board-factory.js";
import API from "@/services/game-api.js";
import { getShiftLocations, useBoardStore } from "@/stores/board.js";
import { useCountdownStore } from "@/stores/countdown.js";
import { usePlayersStore } from "@/stores/players.js";

import * as action from "@/model/player.js";

const OFFLINE = "offline";
const ONLINE = "online";

export const stateFactory = () => ({
    nextAction: null,
    objectiveId: -1,
    mode: OFFLINE,
    serverComputationMethods: [],
    turnProgressionTimeout: 0,
});

export const useGameStore = defineStore("game", {
    state: stateFactory,
    getters: {
        currentPlayer: (state) => {
            const playersStore = usePlayersStore();
            if (state.nextAction) {
                return playersStore.find(state.nextAction.playerId);
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
        computationMethods: (state) => {
            const playersStore = usePlayersStore();
            if (state.mode === ONLINE) {
                return state.serverComputationMethods;
            } else {
                if (playersStore.hasWasmPlayer) {
                    return [];
                } else {
                    return ["wasm"];
                }
            }
        },
    },
    actions: {
        leaveOnlineGame() {
            if (this.isOnline) {
                const playersStore = usePlayersStore();
                API.resetHandlers();
                API.stopPolling();
                playersStore.removeAllClientPlayers();
                this.offline();
            }
        },
        playOnline() {
            const playersStore = usePlayersStore();
            API.errorHandler = (error) => handleError(error);
            API.stateObserver = (apiState) => this.updateFromApi(apiState);
            API.activatePolling();
            this.online();
            playersStore.update([]);
            if (this.computationMethods.length === 0) {
                API.fetchComputationMethods((responseList) => {
                    this.setComputationMethods(responseList);
                });
            }
            playersStore.enterGame();
        },
        playOffline(size = 7) {
            const playersStore = usePlayersStore();
            const boardStore = useBoardStore();
            this.leaveOnlineGame();
            this.$reset();
            playersStore.update([]);

            const board = generateBoard(size);
            const boardState = {
                maze: board,
                enabledShiftLocations: getShiftLocations(size),
                players: [],
            };
            boardStore.update(boardState);
            playersStore.enterGame(null);
            boardStore.updatePlayers(playersStore.all);

            const objectiveMazeCardId = chooseRandomObjective();
            this.updateObjective(objectiveMazeCardId);
        },
        updateFromApi(newState) {
            const playersStore = usePlayersStore();
            const boardStore = useBoardStore();
            this.updateObjective(newState.objectiveMazeCardId);
            this.updateNextAction(newState.nextAction);
            playersStore.update(newState.players);
            const boardState = {
                maze: newState.maze,
                enabledShiftLocations: newState.enabledShiftLocations,
                players: newState.players,
            };
            boardStore.update(boardState);
        },
        move(moveAction) {
            const playersStore = usePlayersStore();
            const boardStore = useBoardStore();
            // already validated
            const targetCard = boardStore.mazeCard(moveAction.targetLocation);
            const sourceCard = playersStore.mazeCard(moveAction.playerId);
            const boardMove = {
                sourceCardId: sourceCard.id,
                targetCardId: targetCard.id,
                playerId: moveAction.playerId,
            };
            boardStore.movePlayer(boardMove);

            const cardChange = { playerId: moveAction.playerId, mazeCardId: targetCard.id };
            playersStore.changePlayersCard(cardChange);
            if (this.isOnline) {
                API.doMove(moveAction.playerId, moveAction.targetLocation);
            } else {
                if (targetCard.id === this.objectiveId) {
                    playersStore.objectiveReached(moveAction.playerId);
                    const objectiveMazeCardId = chooseRandomObjective();
                    this.updateObjective(objectiveMazeCardId);
                }
                const allPlayers = playersStore.all;
                const currentPlayerId = this.nextAction.playerId;
                const currentIndex = allPlayers.findIndex(
                    (player) => player.id === currentPlayerId,
                );
                const nextPlayerId = allPlayers[(currentIndex + 1) % allPlayers.length].id;
                this.continueTurnProgression({
                    playerId: nextPlayerId,
                    action: action.SHIFT_ACTION,
                });
            }
        },
        shift(shiftAction) {
            const playersStore = usePlayersStore();
            const boardStore = useBoardStore();
            if (this.isOnline) {
                API.doShift(
                    shiftAction.playerId,
                    shiftAction.location,
                    shiftAction.leftoverRotation,
                    () => {},
                );
            }

            const shiftLocation = shiftAction.location;
            const oppositeLocation = boardStore.oppositeLocation(shiftLocation);
            const pushedOutCard = boardStore.mazeCard(oppositeLocation);
            const pushedOutPlayerIds = [...pushedOutCard.playerIds];
            const leftoverCard = boardStore.leftoverMazeCard;
            boardStore.shift(shiftAction);
            for (let playerId of pushedOutPlayerIds) {
                const cardChange = { playerId: playerId, mazeCardId: leftoverCard.id };
                playersStore.changePlayersCard(cardChange);
            }

            if (this.isOffline) {
                this.continueTurnProgression({
                    playerId: this.nextAction.playerId,
                    action: action.MOVE_ACTION,
                });
            }
        },
        playerWasRemoved(playerId) {
            if (this.isOffline) {
                if (this.nextAction.playerId === playerId) {
                    const playersStore = usePlayersStore();
                    const allPlayers = playersStore.all;
                    if (allPlayers.length > 0) {
                        /* In offline mode, there are at maximum two players (user and wasm). Hence,
                           it is ok to pick player with index 0 here */
                        this.continueTurnProgression({
                            playerId: allPlayers[0].id,
                            action: action.SHIFT_ACTION,
                        });
                    } else {
                        this.abortTurnProgression();
                    }
                }
            }
        },
        playerWasAdded() {
            if (this.isOffline) {
                const playersStore = usePlayersStore();
                const allPlayers = playersStore.all;
                if (allPlayers.length == 1) {
                    this.continueTurnProgression({
                        playerId: allPlayers[0].id,
                        action: action.SHIFT_ACTION,
                    });
                }
            }
        },
        continueTurnProgression(nextPlayerAction) {
            if (this.turnProgressionTimeout > 0) {
                clearTimeout(this.turnProgressionTimeout);
                this.setTurnProgressionTimeout(0);
            }
            const prepareAction = {
                playerId: nextPlayerAction.playerId,
                action: action.PREPARE_PREFIX + nextPlayerAction.action,
            };
            this.updateNextAction(prepareAction);
            const timeout = setTimeout(() => this.updateNextAction(nextPlayerAction), 800);
            this.setTurnProgressionTimeout(timeout);
        },
        abortTurnProgression() {
            if (this.turnProgressionTimeout > 0) {
                clearTimeout(this.turnProgressionTimeout);
                this.setTurnProgressionTimeout(0);
            }
            this.updateNextAction(null);
        },
        updateObjective(newObjectiveId) {
            this.objectiveId = newObjectiveId;
        },
        updateNextAction(newAction) {
            this.nextAction = newAction;
            const countdownStore = useCountdownStore();
            countdownStore.nextActionUpdated(newAction);
        },
        offline() {
            this.mode = OFFLINE;
        },
        online() {
            this.mode = ONLINE;
        },
        setComputationMethods(computationMethods) {
            this.serverComputationMethods = computationMethods;
        },
        setTurnProgressionTimeout(identifier) {
            this.turnProgressionTimeout = identifier;
        },
    },
});

function handleError(error) {
    const gameStore = useGameStore();
    if (error.response) {
        if (error.response.data.key === "GAME_NOT_FOUND") {
            console.log("Game not found, resetting.");
            gameStore.playOffline();
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

function chooseRandomObjective() {
    const playersStore = usePlayersStore();
    const boardStore = useBoardStore();
    const mazeCardIds = boardStore.allIds;
    const playerCardIds = playersStore.all.map((player) => player.mazeCardId);
    let objectiveMazeCardId;
    do {
        objectiveMazeCardId = randomChoice(mazeCardIds);
    } while (playerCardIds.includes(objectiveMazeCardId));
    return objectiveMazeCardId;
}

function randomChoice(array) {
    return array[Math.floor(Math.random() * array.length)];
}
