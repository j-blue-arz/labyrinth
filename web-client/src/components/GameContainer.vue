<template>
    <div class="game-container">
        <interactive-board
            @move-piece="onMovePlayerPiece"
            @perform-shift="onInsertCard"
            :game="game"
            :user-player-id="userPlayerId"
            ref="interactive-board"
            class="game-container__main-content"
        />
        <wasm-player
            @move-piece="onMovePlayerPiece"
            @perform-shift="onInsertCard"
            :game="game"
            :player-id="wasmPlayerId"
        />
        <score-board :players="players" class="game-container__score" />
        <game-menu
            :api="api"
            :game="game"
            :player-manager="playerManager"
            @enter-game="enterGame"
            @leave-game="leaveGame"
            @enter-wasm="addWasmPlayer"
            @remove-wasm="removeWasmPlayer"
            @called-api-method="startPolling"
            class="game-container__menu"
        />
    </div>
</template>

<script>
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import GameMenu from "@/components/GameMenu.vue";
import ScoreBoard from "@/components/ScoreBoard.vue";
import WasmPlayer from "@/components/WasmPlayer.vue";
import Game from "@/model/game.js";
import GameApi from "@/api/gameApi.js";
import PlayerManager from "@/model/playerManager.js";
import { setInterval, clearInterval } from "timers";

export default {
    name: "game-container",
    components: {
        InteractiveBoard,
        GameMenu,
        ScoreBoard,
        WasmPlayer
    },
    data() {
        return {
            game: new Game(),
            playerManager: null,
            timer: 0,
            api: new GameApi(location.protocol + "//" + location.host)
        };
    },
    computed: {
        players: function() {
            return this.game.getPlayers();
        },
        userPlayerId: function() {
            return this.playerManager.getUserPlayer();
        },
        wasmPlayerId: function() {
            return this.playerManager.getWasmPlayer();
        }
    },
    methods: {
        onInsertCard: function(event) {
            this.game.leftoverMazeCard.rotation = event.leftoverRotation;
            this.stopPolling();
            this.api
                .doShift(event.playerId, event.location, event.leftoverRotation)
                .then(() => this.game.shift(event.location))
                .catch(this.handleError)
                .then(this.startPolling);
        },
        onMovePlayerPiece: function(event) {
            this.game.move(event.playerId, event.targetLocation);
            this.stopPolling();
            this.api
                .doMove(event.playerId, event.targetLocation)
                .catch(this.handleError)
                .then(this.startPolling);
        },
        handleError: function(error) {
            if (!this.api.errorWasThrownByCancel(error)) {
                console.error(error);
            }
        },
        stopPolling() {
            if (this.timer !== 0) {
                clearInterval(this.timer);
                this.timer = 0;
                this.api.cancelAllFetches();
            }
        },
        startPolling() {
            this.stopPolling();
            if (this.timer === 0) {
                this.fetchApiState();
                this.timer = setInterval(this.fetchApiState, 800);
            }
        },
        fetchApiState: function() {
            this.api
                .fetchState()
                .then(this.createGameFromApi)
                .catch(this.handleError);
        },
        createGameFromApi: function(apiResponse) {
            this.game.createFromApi(apiResponse.data);
            if (this.playerManager.hasUserPlayer) {
                let userPlayerId = this.playerManager.getUserPlayer();
                this.game.getPlayer(userPlayerId).isUser = true;
            }
        },
        enterGame: function() {
            if (this.playerManager.canUserEnterGame()) {
                this.api
                    .doAddPlayer()
                    .then(apiResponse => {
                        let userPlayerId = parseInt(apiResponse.data);
                        this.playerManager.addUserPlayer(userPlayerId);
                    })
                    .catch(this.handleError)
                    .then(this.startPolling);
            }
        },
        leaveGame: function() {
            if (this.playerManager.hasUserPlayer()) {
                let playerId = this.playerManager.getUserPlayer();
                this.api
                    .removePlayer(playerId)
                    .catch(this.handleError)
                    .then(this.startPolling);
                this.playerManager.removeUserPlayer();
            }
        },
        addWasmPlayer: function() {
            if (this.playerManager.canAddWasmPlayer()) {
                this.api
                    .doAddPlayer()
                    .then(apiResponse => {
                        let userPlayerId = parseInt(apiResponse.data);
                        this.playerManager.addWasmPlayer(userPlayerId);
                    })
                    .catch(this.handleError)
                    .then(this.startPolling);
            }
        },
        removeWasmPlayer: function() {
            if (this.playerManager.hasWasmPlayer()) {
                let playerId = this.playerManager.getWasmPlayer();
                this.api
                    .removePlayer(playerId)
                    .catch(this.handleError)
                    .then(this.startPolling);
                this.playerManager.removeWasmPlayer();
            }
        },
        useStorage: function() {
            return process.env.NODE_ENV === "production";
        }
    },
    created: function() {
        this.playerManager = new PlayerManager(this.api, this.useStorage());
        if (this.useStorage() && sessionStorage.playerId) {
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
    },
    beforeDestroy() {
        clearInterval(this.timer);
    }
};
</script>

<style lang="scss">
.game-container {
    box-sizing: border-box;
    width: 100%;
    height: 100%;
    display: flex;
    position: relative;
    justify-content: space-around;
    align-items: flex-start;
    align-content: flex-start;

    &__main-content {
        flex: 1 100%;
        order: 1;
    }

    &__score {
        order: 2;
    }

    &__menu {
        order: 3;
    }
}

@media all and (orientation: landscape) {
    .game-container {
        flex-flow: column wrap;
    }

    .game-container__main-content {
        height: 100%;
    }
}

@media all and (orientation: portrait) {
    .game-container {
        flex-flow: row wrap;
    }

    .game-container__main-content {
        width: 100%;
    }
}
</style>
