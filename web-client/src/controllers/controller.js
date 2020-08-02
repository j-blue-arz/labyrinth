import Game from "@/model/game.js";
import GameApi from "@/api/gameApi.js";
import PlayerManager from "@/model/playerManager.js";
import { setInterval, clearInterval } from "timers";
import Player from "@/model/player";
import WasmPlayer from "@/model/wasmPlayer";

export default class Controller {
    constructor(useStorage) {
        this.game = new Game();
        this.playerManager = null;
        this.timer = 0;
        this.api = new GameApi(location.protocol + "//" + location.host);
        this.playerManager = new PlayerManager(this.api, useStorage);
        this.computationMethods = [];
    }

    initialize(useStorage) {
        if (useStorage && sessionStorage.playerId) {
            let userPlayerId = parseInt(sessionStorage.playerId);
            this.api.fetchState().then(() => {
                this.createGameFromApi();
                if (!this.game.hasPlayer(userPlayerId)) {
                    this.enterGame();
                } else {
                    this.playerManager.addUserPlayer(userPlayerId);
                }
            });
        } else {
            this.enterGame();
        }
        this._initComputationMethods();
    }

    _initComputationMethods() {
        this.api
            .fetchComputationMethods()
            .then(methodsResult => {
                this.computationMethods = methodsResult.data;
            })
            .catch(this.handleError);
    }

    onInsertCard(event) {
        this.game.leftoverMazeCard.rotation = event.leftoverRotation;
        this.stopPolling();
        this.api
            .doShift(event.playerId, event.location, event.leftoverRotation)
            .then(() => this.game.shift(event.location))
            .catch(this.handleError)
            .then(this.startPolling);
    }

    onMovePlayerPiece(event) {
        this.game.move(event.playerId, event.targetLocation);
        this.stopPolling();
        this.api
            .doMove(event.playerId, event.targetLocation)
            .catch(this.handleError)
            .then(this.startPolling);
    }

    handleError(error) {
        if (!this.api.errorWasThrownByCancel(error)) {
            console.error(error);
        }
    }

    stopPolling() {
        if (this.timer !== 0) {
            clearInterval(this.timer);
            this.timer = 0;
            this.api.cancelAllFetches();
        }
    }

    startPolling() {
        this.stopPolling();
        if (this.timer === 0) {
            this.fetchApiState();
            this.timer = setInterval(this.fetchApiState, 800);
        }
    }

    fetchApiState() {
        this.api
            .fetchState()
            .then(this.createGameFromApi)
            .catch(this.handleError);
    }

    createGameFromApi(apiResponse) {
        this.game.createFromApi(apiResponse.data);
        if (this.playerManager.hasUserPlayer) {
            let userPlayerId = this.playerManager.getUserPlayer();
            this.game.getPlayer(userPlayerId).isUser = true;
        }
    }

    enterGame() {
        if (this.playerManager.canUserEnterGame()) {
            this.stopPolling();
            this.api
                .doAddPlayer()
                .then(apiResponse => {
                    let userPlayer = Player.newFromApi(apiResponse.data);
                    userPlayer.isUser = true;
                    this.game.addPlayer(userPlayer);
                    this.playerManager.addUserPlayer(userPlayer.id);
                })
                .catch(this.handleError)
                .then(this.startPolling);
        }
    }

    leaveGame() {
        if (this.playerManager.hasUserPlayer()) {
            let playerId = this.playerManager.getUserPlayer();
            this.api
                .removePlayer(playerId)
                .catch(this.handleError)
                .then(this.startPolling);
            this.playerManager.removeUserPlayer();
        }
    }

    addWasmPlayer() {
        if (this.playerManager.canAddWasmPlayer()) {
            this.stopPolling();
            this.api
                .doAddPlayer()
                .then(apiResponse => {
                    let playerId = parseInt(apiResponse.data);
                    let wasmPlayer = new WasmPlayer(
                        playerId,
                        this.game,
                        this.performShift,
                        this.performMove
                    );
                    wasmPlayer.fillFromApi(apiResponse.data);
                    this.game.addPlayer(wasmPlayer);
                    this.playerManager.addWasmPlayer(wasmPlayer.id);
                })
                .catch(this.handleError)
                .then(this.startPolling);
        }
    }

    removeWasmPlayer() {
        if (this.playerManager.hasWasmPlayer()) {
            let playerId = this.playerManager.getWasmPlayer();
            this.api
                .removePlayer(playerId)
                .catch(this.handleError)
                .then(this.startPolling);
            this.playerManager.removeWasmPlayer();
        }
    }

    addComputer(computeMethod) {
        this.api
            .doAddComputerPlayer(computeMethod)
            .catch(this.handleError)
            .then(this.startPolling);
    }

    removeComputer(playerId) {
        this.api
            .removePlayer(playerId)
            .catch(this.handleError)
            .then(this.startPolling);
    }

    restartWithSize(size) {
        this.api
            .changeGame(size)
            .catch(this.handleError)
            .then(this.startPolling);
    }

    beforeDestroy() {
        clearInterval(this.timer);
    }
}
