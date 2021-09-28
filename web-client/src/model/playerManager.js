const NOT_PARTICIPATING = -1;

export default class PlayerManager {
    constructor() {
        this._userPlayer = NOT_PARTICIPATING;
        this._wasmPlayer = NOT_PARTICIPATING;
    }

    addUserPlayerId(playerId) {
        this._userPlayer = playerId;
    }

    removeUserPlayer() {
        this._userPlayer = NOT_PARTICIPATING;
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
    }

    addWasmPlayerId(playerId) {
        this._wasmPlayer = playerId;
    }

    getWasmPlayerId() {
        return this._wasmPlayer;
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
