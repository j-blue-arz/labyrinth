const NOT_PARTICIPATING = -1;

export default class PlayerManager {
    constructor(useStorage) {
        this._userPlayer = NOT_PARTICIPATING;
        this._wasmPlayer = NOT_PARTICIPATING;
        this._useStorage = useStorage;
        if (useStorage) {
            if (sessionStorage.userPlayerId) {
                this._userPlayer = parseInt(sessionStorage.userPlayerId);
            }
            if (sessionStorage.wasmPlayerId) {
                this._wasmPlayer = parseInt(sessionStorage.wasmPlayerId);
            }
        }
    }

    addUserPlayerId(playerId) {
        this._userPlayer = playerId;
        if (this._useStorage) {
            sessionStorage.userPlayerId = playerId;
        }
    }

    removeUserPlayer() {
        this._userPlayer = NOT_PARTICIPATING;
        if (this._useStorage) {
            sessionStorage.userPlayerId = NOT_PARTICIPATING;
        }
    }

    getUserPlayerId() {
        return this._userPlayer;
    }

    hasUserPlayer() {
        return this._userPlayer !== NOT_PARTICIPATING;
    }

    canUserEnterGame() {
        return this._userPlayer === NOT_PARTICIPATING;
    }

    canAddWasmPlayerId() {
        return this._wasmPlayer === NOT_PARTICIPATING;
    }

    hasWasmPlayer() {
        return this._wasmPlayer !== NOT_PARTICIPATING;
    }

    removeWasmPlayer() {
        this._wasmPlayer = NOT_PARTICIPATING;
        if (this._useStorage) {
            sessionStorage.wasmPlayerId = NOT_PARTICIPATING;
        }
    }

    addWasmPlayerId(playerId) {
        this._wasmPlayer = playerId;
        if (this._useStorage) {
            sessionStorage.wasmPlayerId = playerId;
        }
    }

    getWasmPlayerId() {
        return this._wasmPlayer;
    }

    hasAnyPlayer() {
        return this.hasWasmPlayer() || this.hasUserPlayer();
    }

    getManagedPlayerIds() {
        let result = [];
        if (this.hasWasmPlayer()) {
            result.push(this.getWasmPlayerId());
        }
        if (this.hasUserPlayer()) {
            result.push(this.getUserPlayerId());
        }
        return result;
    }

    hasPlayerId(playerId) {
        return this.getUserPlayerId() === playerId || this.getWasmPlayerId() === playerId;
    }

    removePlayerId(playerId) {
        if (this.getUserPlayerId() === playerId) {
            this.removeUserPlayer();
        }
        if (this.getWasmPlayerId() === playerId) {
            this.removeWasmPlayer();
        }
    }
}
