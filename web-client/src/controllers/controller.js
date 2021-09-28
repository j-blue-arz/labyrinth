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
        this._polling_timer = 0;
        this._playerManager = new PlayerManager();
        this._computationMethods = [];
        this._turnCountdown = new CountdownTimer(TURN_SECONDS);

        this.handleError = this.handleError.bind(this);
        this._startPolling = this._startPolling.bind(this);
    }

    initialize() {
        this.enterGame();
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
        API.doShift(shiftAction.playerId, shiftAction.location, shiftAction.leftoverRotation)
            .then(() => this._game.shift(shiftAction.location))
            .catch(this.handleError)
            .then(this._startPolling);
    }

    performMove(moveAction) {
        // already validated, so we can alter the game state directly
        this._game.move(moveAction.playerId, moveAction.targetLocation);
        this._stopPolling();
        API.doMove(moveAction.playerId, moveAction.targetLocation)
            .catch(this.handleError)
            .then(this._startPolling);
    }

    handleError(error) {
        if (!API.errorWasThrownByCancel(error)) {
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
            API.cancelAllFetches();
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
        API.fetchState()
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
            API.doAddPlayer()
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
            API.removePlayer(playerId)
                .catch(this.handleError)
                .then(this._startPolling);
            this._playerManager.removeUserPlayer();
        }
    }

    addWasmPlayer() {
        if (this._playerManager.canAddWasmPlayerId()) {
            this._stopPolling();
            API.doAddPlayer()
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
            API.removePlayer(playerId)
                .catch(this.handleError)
                .then(this._startPolling);
            this._playerManager.removeWasmPlayer();
        }
    }

    removeManagedPlayer(playerId) {
        if (this._playerManager.hasPlayerId(playerId)) {
            API.removePlayer(playerId)
                .catch(this.handleError)
                .then(this._startPolling);
            this._playerManager.removePlayerId(playerId);
        }
    }

    addBot(computeMethod) {
        API.doAddBot(computeMethod)
            .catch(this.handleError)
            .then(this._startPolling);
    }

    removeBot(playerId) {
        API.removePlayer(playerId)
            .catch(this.handleError)
            .then(this._startPolling);
    }

    restartWithSize(size) {
        API.changeGame(size)
            .catch(this.handleError)
            .then(this._startPolling);
    }

    beforeDestroy() {
        let playerIds = this._playerManager.getManagedPlayerIds();
        for (let playerId of playerIds) {
            API.removePlayer(playerId);
        }
        clearInterval(this._polling_timer);
    }

    changeUserPlayerName(newName) {
        if (this._playerManager.hasUserPlayer()) {
            const userPlayerId = this._playerManager.getUserPlayerId();
            let userPlayer = this._game.getPlayer(userPlayerId);
            userPlayer.playerName = newName;
            API.changePlayerName(userPlayerId, newName).catch(this.handleError);
        }
    }

    get game() {
        return this._game;
    }

    get playerManager() {
        return this._playerManager;
    }

    getComputationMethods() {
        return this._computationMethods;
    }

    _initComputationMethods() {
        API.fetchComputationMethods()
            .then(methodsResult => {
                this._computationMethods = methodsResult.data;
            })
            .catch(this.handleError);
    }

    get turnCountdown() {
        return this._turnCountdown;
    }
}
