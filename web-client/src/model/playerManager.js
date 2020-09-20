const NOT_PARTICIPATING = -1;

export default class PlayerManager {
    constructor(useStorage) {
        this.userPlayer = NOT_PARTICIPATING;
        this.wasmPlayer = NOT_PARTICIPATING;
        this._useStorage = useStorage;
        if (useStorage) {
            if (sessionStorage.userPlayerId) {
                this.userPlayer = parseInt(sessionStorage.userPlayerId);
            }
            if (sessionStorage.wasmPlayerId) {
                this.wasmPlayer = parseInt(sessionStorage.wasmPlayerId);
            }
        }
    }

    addUserPlayer(playerId) {
        this.userPlayer = playerId;
        if (this._useStorage) {
            sessionStorage.userPlayerId = playerId;
        }
    }

    removeUserPlayer() {
        this.userPlayer = NOT_PARTICIPATING;
        if (this._useStorage) {
            sessionStorage.userPlayerId = NOT_PARTICIPATING;
        }
    }

    getUserPlayer() {
        return this.userPlayer;
    }

    hasUserPlayer() {
        return this.userPlayer !== NOT_PARTICIPATING;
    }

    canUserEnterGame() {
        return this.userPlayer === NOT_PARTICIPATING;
    }

    canAddWasmPlayer() {
        return this.wasmPlayer === NOT_PARTICIPATING;
    }

    hasWasmPlayer() {
        return this.wasmPlayer !== NOT_PARTICIPATING;
    }

    removeWasmPlayer() {
        this.wasmPlayer = NOT_PARTICIPATING;
        if (this._useStorage) {
            sessionStorage.wasmPlayerId = NOT_PARTICIPATING;
        }
    }

    addWasmPlayer(playerId) {
        this.wasmPlayer = playerId;
        if (this._useStorage) {
            sessionStorage.wasmPlayerId = playerId;
        }
    }

    getWasmPlayer() {
        return this.wasmPlayer;
    }

    hasAnyPlayer() {
        return this.hasWasmPlayer() || this.hasUserPlayer();
    }

    getManagedPlayers() {
        let result = [];
        if (this.hasWasmPlayer()) {
            result.push(this.getWasmPlayer());
        }
        if (this.hasUserPlayer()) {
            result.push(this.getUserPlayer());
        }
        return result;
    }

    hasPlayer(playerId) {
        return this.getUserPlayer() === playerId || this.getWasmPlayer() === playerId;
    }

    removePlayer(playerId) {
        if (this.getUserPlayer() === playerId) {
            this.removeUserPlayer();
        }
        if (this.getWasmPlayer() === playerId) {
            this.removeWasmPlayer();
        }
    }
}
