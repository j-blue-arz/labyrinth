import Game from "@/model/game.js";
import GameApi from "@/api/gameApi.js";
import PlayerManager from "@/model/playerManager.js";
import { setInterval, clearInterval } from "timers";
import Player from "@/model/player";
import WasmPlayer from "@/model/wasmPlayer";

export default class Controller {
    constructor(useStorage) {
        this._game = new Game();
        this._timer = 0;
        this._api = new GameApi(location.protocol + "//" + location.host);
        this._playerManager = new PlayerManager(useStorage);
        this._computationMethods = [];

        this.handleError = this.handleError.bind(this);
        this.startPolling = this.startPolling.bind(this);
    }

    initialize() {
        if (this._playerManager.hasAnyPlayer()) {
            this._api
                .fetchState() //
                .then(state => {
                    this.createGameFromApi(state);
                    this._updateUserPlayer();
                    this._updateWasmPlayer();
                    if (!this._playerManager.hasAnyPlayer()) {
                        this.enterGame();
                    } else {
                        this.startPolling();
                    }
                })
                .catch(this.handleError);
        } else {
            this.enterGame();
        }
        this._initComputationMethods();
    }

    _updateUserPlayer() {
        if (!this._game.hasPlayer(this._playerManager.getUserPlayer())) {
            this._playerManager.removeUserPlayer();
        } else {
            let userPlayerId = this._playerManager.getUserPlayer();
            this._game.getPlayer(userPlayerId).isUser = true;
        }
    }

    _updateWasmPlayer() {
        let wasmPlayerId = this._playerManager.getWasmPlayer();
        if (!this._game.hasPlayer(wasmPlayerId)) {
            this._playerManager.removeWasmPlayer();
        } else {
            let wasmPlayer = new WasmPlayer(
                wasmPlayerId,
                this._game,
                shiftAction => this.performShift(shiftAction),
                moveAction => this.performMove(moveAction)
            );
            let existingPlayer = this._game.getPlayer(wasmPlayerId);
            wasmPlayer.fillFromPlayer(existingPlayer);
            this._game.replaceWithPlayer(wasmPlayer);
        }
    }

    performShift(shiftAction) {
        this._game.leftoverMazeCard.rotation = shiftAction.leftoverRotation;
        this.stopPolling();
        this._api
            .doShift(shiftAction.playerId, shiftAction.location, shiftAction.leftoverRotation)
            .then(() => this._game.shift(shiftAction.location))
            .catch(this.handleError)
            .then(this.startPolling);
    }

    performMove(moveAction) {
        // already validated, so we can alter the game state directly
        this._game.move(moveAction.playerId, moveAction.targetLocation);
        this.stopPolling();
        this._api
            .doMove(moveAction.playerId, moveAction.targetLocation)
            .catch(this.handleError)
            .then(this.startPolling);
    }

    handleError(error) {
        if (!this._api.errorWasThrownByCancel(error)) {
            if (error.response) {
                if (error.response.data.key === "GAME_NOT_FOUND") {
                    console.log("Game not found, resetting.");
                    this._playerManager.removeWasmPlayer();
                    this._playerManager.removeUserPlayer();
                    this._game.reset();
                    this.stopPolling();
                } else {
                    console.error("Response error", error.response.data);
                }
            } else if (error.request) {
                this.stopPolling();
                console.error("Request error", error.request);
            } else {
                console.error("Error", error.message);
            }
        }
    }

    stopPolling() {
        if (this._timer !== 0) {
            clearInterval(this._timer);
            this._timer = 0;
            this._api.cancelAllFetches();
        }
    }

    startPolling() {
        this.stopPolling();
        if (this._timer === 0) {
            this.fetchApiState();
            this._timer = setInterval(() => this.fetchApiState(), 800);
        }
    }

    fetchApiState() {
        this._api
            .fetchState()
            .then(response => this.createGameFromApi(response))
            .catch(this.handleError);
    }

    createGameFromApi(apiResponse) {
        this._game.createFromApi(apiResponse.data);
        if (this._playerManager.hasUserPlayer()) {
            let userPlayerId = this._playerManager.getUserPlayer();
            let userPlayer = this._game.getPlayer(userPlayerId);
            if (userPlayer) {
                userPlayer.isUser = true;
            } else {
                this._playerManager.removeUserPlayer();
            }
        }
        if (this._playerManager.hasWasmPlayer()) {
            let wasmPlayer = this._game.getPlayer(this._playerManager.getWasmPlayer());
            if (!wasmPlayer) {
                this._playerManager.removeWasmPlayer();
            }
        }
    }

    enterGame() {
        if (this._playerManager.canUserEnterGame()) {
            this.stopPolling();
            this._api
                .doAddPlayer()
                .then(apiResponse => {
                    let userPlayer = new Player(apiResponse.data.id);
                    userPlayer.isUser = true;
                    this._game.addPlayerFromApi(apiResponse.data, userPlayer);
                    this._playerManager.addUserPlayer(userPlayer.id);
                })
                .catch(this.handleError)
                .then(this.startPolling);
        }
    }

    leaveGame() {
        if (this._playerManager.hasUserPlayer()) {
            let playerId = this._playerManager.getUserPlayer();
            this._api
                .removePlayer(playerId)
                .catch(this.handleError)
                .then(this.startPolling);
            this._playerManager.removeUserPlayer();
        }
    }

    addWasmPlayer() {
        if (this._playerManager.canAddWasmPlayer()) {
            this.stopPolling();
            this._api
                .doAddPlayer()
                .then(apiResponse => {
                    let playerId = parseInt(apiResponse.data.id);
                    let wasmPlayer = new WasmPlayer(
                        playerId,
                        this._game,
                        shiftAction => this.performShift(shiftAction),
                        moveAction => this.performMove(moveAction)
                    );
                    this._game.addPlayerFromApi(apiResponse.data, wasmPlayer);
                    this._playerManager.addWasmPlayer(wasmPlayer.id);
                })
                .catch(this.handleError)
                .then(this.startPolling);
        }
    }

    removeWasmPlayer() {
        if (this._playerManager.hasWasmPlayer()) {
            let playerId = this._playerManager.getWasmPlayer();
            this._api
                .removePlayer(playerId)
                .catch(this.handleError)
                .then(this.startPolling);
            this._playerManager.removeWasmPlayer();
        }
    }

    addComputer(computeMethod) {
        this._api
            .doAddComputerPlayer(computeMethod)
            .catch(this.handleError)
            .then(this.startPolling);
    }

    removeComputer(playerId) {
        this._api
            .removePlayer(playerId)
            .catch(this.handleError)
            .then(this.startPolling);
    }

    restartWithSize(size) {
        this._api
            .changeGame(size)
            .catch(this.handleError)
            .then(this.startPolling);
    }

    beforeDestroy() {
        let playerIds = this._playerManager.getManagedPlayers();
        for (let playerId of playerIds) {
            this._api.removePlayer(playerId);
        }
        clearInterval(this._timer);
    }

    getGame() {
        return this._game;
    }

    getPlayerManager() {
        return this._playerManager;
    }

    getComputationMethods() {
        return this._computationMethods;
    }

    _initComputationMethods() {
        this._api
            .fetchComputationMethods()
            .then(methodsResult => {
                this._computationMethods = methodsResult.data;
            })
            .catch(this.handleError);
    }
}
