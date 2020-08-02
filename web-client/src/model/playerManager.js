const NOT_PARTICIPATING = -1;

export default class PlayerManager {
    constructor(gameApi, useStorage) {
        this.userPlayer = NOT_PARTICIPATING;
        this.wasmPlayer = NOT_PARTICIPATING;
        this.api = gameApi;
        this.useStorage = useStorage;
    }

    addUserPlayer(playerId) {
        this.userPlayer = playerId;
        if (this.useStorage()) {
            sessionStorage.playerId = playerId;
        }
    }

    removeUserPlayer() {
        this.userPlayer = NOT_PARTICIPATING;
        if (this.useStorage()) {
            sessionStorage.playerId = NOT_PARTICIPATING;
        }
    }

    getUserPlayer() {
        return this.userPlayer;
    }

    hasUserPlayer() {
        return this.userPlayer !== NOT_PARTICIPATING;
    }

    canAddWasmPlayer() {
        return this.wasmPlayer === NOT_PARTICIPATING;
    }

    canUserEnterGame() {
        return this.userPlayer === NOT_PARTICIPATING;
    }
}
