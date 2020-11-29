import Game from "@/model/game.js";
import GameApi from "@/api/gameApi.js";
import PlayerManager from "@/model/playerManager.js";
import { setInterval, clearInterval } from "timers";
import Player from "@/model/player";
import WasmPlayer from "@/model/wasmPlayer";
import CountdownTimer from "@/model/countdown";

const POLL_INTERVAL_MS = 850;
const TURN_SECONDS = 30;

export default class Controller {
    constructor(useStorage) {
        this._game = new Game();
        this._polling_timer = 0;
        this._api = new GameApi(location.protocol + "//" + location.host);
        this._playerManager = new PlayerManager(useStorage);
        this._computationMethods = [];
        this._turnCountdown = new CountdownTimer(TURN_SECONDS);

        this.handleError = this.handleError.bind(this);
        this._startPolling = this._startPolling.bind(this);
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
                        this._startPolling();
                    }
                })
                .catch(this.handleError);
        } else {
            this.enterGame();
        }
        this._initComputationMethods();
    }

    _updateUserPlayer() {
        if (!this._game.hasPlayer(this._playerManager.getUserPlayerId())) {
            this._playerManager.removeUserPlayer();
        } else {
            let userPlayerId = this._playerManager.getUserPlayerId();
            this._game.getPlayer(userPlayerId).isUser = true;
        }
    }

    _updateWasmPlayer() {
        let wasmPlayerId = this._playerManager.getWasmPlayerId();
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
        this._stopPolling();
        this._api
            .doShift(shiftAction.playerId, shiftAction.location, shiftAction.leftoverRotation)
            .then(() => this._game.shift(shiftAction.location))
            .catch(this.handleError)
            .then(this._startPolling);
    }

    performMove(moveAction) {
        // already validated, so we can alter the game state directly
        this._game.move(moveAction.playerId, moveAction.targetLocation);
        this._stopPolling();
        this._api
            .doMove(moveAction.playerId, moveAction.targetLocation)
            .catch(this.handleError)
            .then(this._startPolling);
    }

    handleError(error) {
        if (!this._api.errorWasThrownByCancel(error)) {
            if (error.response) {
                if (error.response.data.key === "GAME_NOT_FOUND") {
                    console.log("Game not found, resetting.");
                    this._playerManager.removeWasmPlayer();
                    this._playerManager.removeUserPlayer();
                    this._game.reset();
                    this._stopPolling();
                } else {
                    console.error("Response error", error.response.data);
                }
            } else if (error.request) {
                this._stopPolling();
                console.error("Request error", error.request);
            } else {
                console.error("Error", error.message);
            }
        }
    }

    _stopPolling() {
        if (this._polling_timer !== 0) {
            clearInterval(this._polling_timer);
            this._polling_timer = 0;
            this._api.cancelAllFetches();
        }
    }

    _startPolling() {
        this._stopPolling();
        if (this._polling_timer === 0) {
            this.fetchApiState();
            this._polling_timer = setInterval(() => this.fetchApiState(), POLL_INTERVAL_MS);
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
            this._stopPolling();
            this._api
                .doAddPlayer()
                .then(apiResponse => {
                    let userPlayer = new Player(apiResponse.data.id);
                    userPlayer.isUser = true;
                    this._game.addPlayerFromApi(apiResponse.data, userPlayer);
                    this._playerManager.addUserPlayerId(userPlayer.id);
                })
                .catch(this.handleError)
                .then(this._startPolling);
        }
    }

    leaveGame() {
        if (this._playerManager.hasUserPlayer()) {
            let playerId = this._playerManager.getUserPlayerId();
            this._api
                .removePlayer(playerId)
                .catch(this.handleError)
                .then(this._startPolling);
            this._playerManager.removeUserPlayer();
        }
    }

    addWasmPlayer() {
        if (this._playerManager.canAddWasmPlayerId()) {
            this._stopPolling();
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
                    this._playerManager.addWasmPlayerId(wasmPlayer.id);
                })
                .catch(this.handleError)
                .then(this._startPolling);
        }
    }

    removeWasmPlayer() {
        if (this._playerManager.hasWasmPlayer()) {
            let playerId = this._playerManager.getWasmPlayerId();
            this._api
                .removePlayer(playerId)
                .catch(this.handleError)
                .then(this._startPolling);
            this._playerManager.removeWasmPlayer();
        }
    }

    removeManagedPlayer(playerId) {
        if (this._playerManager.hasPlayerId(playerId)) {
            this._api
                .removePlayer(playerId)
                .catch(this.handleError)
                .then(this._startPolling);
            this._playerManager.removePlayerId(playerId);
        }
    }

    addComputer(computeMethod) {
        this._api
            .doAddComputerPlayer(computeMethod)
            .catch(this.handleError)
            .then(this._startPolling);
    }

    removeComputer(playerId) {
        this._api
            .removePlayer(playerId)
            .catch(this.handleError)
            .then(this._startPolling);
    }

    restartWithSize(size) {
        this._api
            .changeGame(size)
            .catch(this.handleError)
            .then(this._startPolling);
    }

    beforeDestroy() {
        let playerIds = this._playerManager.getManagedPlayerIds();
        for (let playerId of playerIds) {
            this._api.removePlayer(playerId);
        }
        clearInterval(this._polling_timer);
    }

    get game() {
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

    get turnCountdown() {
        return this._turnCountdown;
    }
}
