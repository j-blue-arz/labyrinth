import Game from "@/model/game.js";
import API from "@/services/game-api.js";
import PlayerManager from "@/model/playerManager.js";
import Player from "@/model/player";
import WasmPlayer from "@/model/wasmPlayer";
import CountdownTimer from "@/model/countdown";

const POLL_INTERVAL_MS = 850;
const TURN_SECONDS = 30;

export default class Controller {
    constructor() {
        this._game = new Game();
        this._playerManager = new PlayerManager();
        this._turnCountdown = new CountdownTimer(TURN_SECONDS);

        this.handleError = this.handleError.bind(this);
        API.errorHandlers.push(error => this.handleError(error));
        API.stateObservers.push(apiState => this.createGameFromApi(apiState));
    }

    initialize() {
        this.enterGame();
    }

    performShift(shiftAction) {
        this._game.leftoverMazeCard.rotation = shiftAction.leftoverRotation;
        API.doShift(shiftAction.playerId, shiftAction.location, shiftAction.leftoverRotation, () =>
            this._game.shift(shiftAction.location)
        );
    }

    performMove(moveAction) {
        // already validated, so we can alter the game state directly
        this._game.move(moveAction.playerId, moveAction.targetLocation);
        API.doMove(moveAction.playerId, moveAction.targetLocation);
    }

    handleError(error) {
        if (error.response) {
            if (error.response.data.key === "GAME_NOT_FOUND") {
                console.log("Game not found, resetting.");
                this._playerManager.removeWasmPlayer();
                this._playerManager.removeUserPlayer();
                this._game.reset();
                API.stopPolling();
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

    createGameFromApi(apiResponse) {
        this._game.createFromApi(apiResponse);
        if (this._playerManager.hasUserPlayer()) {
            let userPlayerId = this._playerManager.getUserPlayerId();
            let userPlayer = this._game.getPlayer(userPlayerId);
            if (userPlayer) {
                userPlayer.isUser = true;
            } else {
                this._playerManager.removeUserPlayer();
            }
        }
        if (this._playerManager.hasWasmPlayer()) {
            let wasmPlayer = this._game.getPlayer(this._playerManager.getWasmPlayerId());
            if (!wasmPlayer) {
                this._playerManager.removeWasmPlayer();
            }
        }
    }

    enterGame() {
        if (this._playerManager.canUserEnterGame()) {
            API.activatePolling();
            API.doAddPlayer(response => {
                let userPlayer = new Player(response.id);
                userPlayer.isUser = true;
                this._game.addPlayerFromApi(response, userPlayer);
                this._playerManager.addUserPlayerId(userPlayer.id);
            });
        }
    }

    leaveGame() {
        if (this._playerManager.hasUserPlayer()) {
            let playerId = this._playerManager.getUserPlayerId();
            API.removePlayer(playerId);
            this._playerManager.removeUserPlayer();
        }
    }

    addWasmPlayer() {
        if (this._playerManager.canAddWasmPlayerId()) {
            API.doAddPlayer(response => {
                let playerId = parseInt(response.id);
                let wasmPlayer = new WasmPlayer(
                    playerId,
                    this._game,
                    shiftAction => this.performShift(shiftAction),
                    moveAction => this.performMove(moveAction)
                );
                this._game.addPlayerFromApi(response, wasmPlayer);
                this._playerManager.addWasmPlayerId(wasmPlayer.id);
            });
        }
    }

    removeWasmPlayer() {
        if (this._playerManager.hasWasmPlayer()) {
            let playerId = this._playerManager.getWasmPlayerId();
            API.removePlayer(playerId);
            this._playerManager.removeWasmPlayer();
        }
    }

    removeManagedPlayer(playerId) {
        if (this._playerManager.hasPlayerId(playerId)) {
            API.removePlayer(playerId);
            this._playerManager.removePlayerId(playerId);
        }
    }

    addBot(computeMethod) {
        API.doAddBot(computeMethod);
    }

    removeBot(playerId) {
        API.removePlayer(playerId);
    }

    restartWithSize(size) {
        API.changeGame(size);
    }

    beforeDestroy() {
        API.stopPolling();
        let playerIds = this._playerManager.getManagedPlayerIds();
        for (let playerId of playerIds) {
            API.removePlayer(playerId);
        }
    }

    changeUserPlayerName(newName) {
        if (this._playerManager.hasUserPlayer()) {
            const userPlayerId = this._playerManager.getUserPlayerId();
            let userPlayer = this._game.getPlayer(userPlayerId);
            userPlayer.playerName = newName;
            API.changePlayerName(userPlayerId, newName);
        }
    }

    get game() {
        return this._game;
    }

    get playerManager() {
        return this._playerManager;
    }

    get turnCountdown() {
        return this._turnCountdown;
    }
}
