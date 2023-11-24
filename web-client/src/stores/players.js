import { defineStore } from "pinia";

import API from "@/services/game-api.js";
import * as action from "@/model/player.js";

import { useBoardStore } from "@/stores/board.js";
import { useGameStore } from "@/stores/game.js";

export const usePlayersStore = defineStore("players", {
    state: () => ({
        byId: {},
        allIds: [],
    }),
    getters: {
        find: (state) => (id) => {
            const player = state.byId[id];
            if (player) {
                const gameStore = useGameStore();
                const nextAction = gameStore.nextAction;
                return {
                    ...player,
                    nextAction: nextAction?.playerId === id ? nextAction.action : action.NO_ACTION,
                };
            } else {
                return undefined;
            }
        },
        all(state) {
            return state.allIds.map((id) => this.find(id));
        },
        findByMazeCard() {
            return function(cardId) {
                return this.all.filter((player) => player.mazeCardId === cardId);
            }
        },
        mazeCard: (state) => (id) => {
            const boardStore = useBoardStore();
            const player = state.byId[id];
            return boardStore.mazeCardById(player.mazeCardId);
        },
        hasUserPlayer: (state) => {
            return state.allIds.some((id) => state.byId[id].isUser);
        },
        userPlayerId: (state) => {
            return state.allIds.find((id) => state.byId[id].isUser);
        },
        userPlayer() {
            return this.find(this.userPlayerId);
        },
        hasWasmPlayer: (state) => {
            return state.allIds.some((id) => state.byId[id].isWasm);
        },
        wasmPlayerId: (state) => {
            return state.allIds.find((id) => state.byId[id].isWasm);
        },
        wasmPlayer() {
            return this.find(this.wasmPlayerId);
        },
        bots() {
            return this.all.filter((player) => player.isBot);
        },
    },
    actions: {
        update(apiPlayers) {
            const apiIds = apiPlayers.map((apiPlayer) => apiPlayer.id);
            const removedPlayerIds = this.allIds.filter((id) => !apiIds.includes(id));
            removedPlayerIds.forEach((playerId) => {
                this.removePlayer(playerId);
            });
            apiPlayers.forEach((apiPlayer) => {
                if (this.allIds.includes(apiPlayer.id)) {
                    this.updatePlayer(apiPlayer);
                } else {
                    this.addPlayer(apiPlayer);
                }
            });
        },
        changePlayersCard(cardChange) {
            this.setPlayerCard(cardChange);
        },
        enterGame() {
            if (!this.hasUserPlayer) {
                const gameStore = useGameStore();
                if (gameStore.isOnline) {
                    API.doAddPlayer((apiPlayer) => {
                        apiPlayer.isUser = true;
                        this.addPlayer(apiPlayer);
                    });
                } else {
                    const boardStore = useBoardStore();
                    const playerMazeCard = boardStore.mazeCard({ row: 0, column: 0 });
                    const player = createPlayer(0);
                    player.isUser = true;
                    player.mazeCardId = playerMazeCard.id;
                    this.addPlayer(player);
                    gameStore.playerWasAdded();
                    boardStore.updatePlayers(this.all);
                }
            }
        },
        leaveGame() {
            if (this.hasUserPlayer) {
                this.removeClientPlayer(this.userPlayerId);
            }
        },
        addWasmPlayer() {
            if (!this.hasWasmPlayer) {
                const gameStore = useGameStore();
                if (gameStore.isOnline) {
                    API.doAddPlayer((apiPlayer) => {
                        apiPlayer.isWasm = true;
                        this.addPlayer(apiPlayer);
                    });
                } else {
                    const boardStore = useBoardStore();
                    const playerMazeCard = boardStore.mazeCard({
                        row: 0,
                        column: boardStore.mazeSize - 1,
                    });
                    const player = createPlayer(1);
                    player.isWasm = true;
                    player.mazeCardId = playerMazeCard.id;
                    this.addPlayer(player);
                    gameStore.playerWasAdded();
                    boardStore.updatePlayers(this.all);
                }
            }
        },
        removeWasmPlayer() {
            if (this.hasWasmPlayer) {
                this.removeClientPlayer(this.wasmPlayerId);
            }
        },
        removeAllClientPlayers() {
            this.removeWasmPlayer();
            this.leaveGame();
        },
        removeClientPlayer(playerId) {
            const boardStore = useBoardStore();
            const gameStore = useGameStore();
            if (this.userPlayerId === playerId || this.wasmPlayerId === playerId) {
                if (gameStore.isOnline) {
                    API.removePlayer(playerId);
                }
                this.removePlayer(playerId);
                gameStore.playerWasRemoved(playerId);
                boardStore.updatePlayers(this.all);
            }
        },
        changeUserPlayerName(newName) {
            const gameStore = useGameStore();
            if (this.hasUserPlayer) {
                const playerId = this.userPlayerId;
                if (gameStore.isOnline) {
                    API.changePlayerName(playerId, newName);
                }
                this.changeName({ id: playerId, name: newName });
            }
        },
        objectiveReached(playerId) {
            this.increaseScore(playerId);
        },
        setPlayerCard(cardChange) {
            this.byId[cardChange.playerId].mazeCardId = cardChange.mazeCardId;
        },
        addPlayer(playerToAdd) {
            let defaultPlayer = newPlayer(playerToAdd.id);
            let player = fillPlayer(defaultPlayer, playerToAdd);
            this.byId[player.id] = player;
            this.allIds.push(player.id);
        },
        removePlayer(id) {
            delete this.byId[id];
            const index = this.allIds.indexOf(id);
            this.allIds.splice(index, 1);
        },
        updatePlayer(player) {
            let existingPlayer = this.byId[player.id];
            let updatedPlayer = fillPlayer(existingPlayer, player);
            this.byId[updatedPlayer.id] = updatedPlayer;
        },
        changeName(nameChange) {
            this.byId[nameChange.id].name = nameChange.name;
        },
        increaseScore(playerId) {
            this.byId[playerId].score += 1;
        },
    },
});

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
        pieceIndex: playerId,
    };
    return player;
}
