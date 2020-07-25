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
            :player-id="userPlayerId"
        />
        <score-board :players="players" class="game-container__score" />
        <game-menu
            v-if="isUsingApi"
            :api="api"
            :game="game"
            :user-player-id="userPlayerId"
            @enter-game="enterGame"
            @leave-game="leaveGame"
            @replace-wasm="replaceWithWasm"
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
import Game, * as actions from "@/model/game.js";
import GameFactory from "@/model/gameFactory.js";
import GameApi from "@/api/gameApi.js";
import { setInterval, clearInterval } from "timers";

const NOT_PARTICIPATING = -1;

export default {
    name: "game-container",
    components: {
        InteractiveBoard,
        GameMenu,
        ScoreBoard,
        WasmPlayer
    },
    props: {
        gameFactory: {
            type: GameFactory,
            required: false,
            default: null
        },
        shouldUseApi: {
            type: Boolean,
            required: false,
            default: true
        }
    },
    data() {
        return {
            game: new Game(),
            userPlayerId: NOT_PARTICIPATING,
            timer: 0,
            api: new GameApi(location.protocol + "//" + location.host)
        };
    },
    computed: {
        isUsingApi: function() {
            return this.useApi();
        },
        players: function() {
            return this.game.getPlayers();
        }
    },
    methods: {
        onInsertCard: function(event) {
            this.game.leftoverMazeCard.rotation = event.leftoverRotation;
            this.stopPolling();
            if (this.useApi()) {
                this.api
                    .doShift(event.location, event.leftoverRotation)
                    .then(() => this.game.shift(event.location))
                    .catch(this.handleError)
                    .then(this.startPolling);
            } else {
                this.game.shift(event.location);
                this.game.nextAction.action = actions.MOVE_ACTION;
                this.game.getPlayer(this.userPlayerId).turnAction = actions.MOVE_ACTION;
            }
        },
        onMovePlayerPiece: function(targetLocation) {
            this.game.move(this.userPlayerId, targetLocation);
            if (this.useApi()) {
                this.stopPolling();
                this.api
                    .doMove(targetLocation)
                    .catch(this.handleError)
                    .then(this.startPolling);
            } else {
                this.game.nextAction.action = actions.SHIFT_ACTION;
                this.game.getPlayer(this.userPlayerId).turnAction = actions.SHIFT_ACTION;
            }
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
            if (this.timer === 0 && this.useApi()) {
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
            this.game.createFromApi(apiResponse.data, this.userPlayerId);
        },
        enterGame: function() {
            this.api
                .doAddPlayer()
                .then(this.addPlayer)
                .catch(this.handleError)
                .then(this.startPolling);
        },
        leaveGame: function() {
            this.api
                .removePlayer(this.userPlayerId)
                .catch(this.handleError)
                .then(this.startPolling);
            this.userPlayerId = NOT_PARTICIPATING;
            if (this.useStorage()) {
                sessionStorage.playerId = this.userPlayerId;
            }
        },
        replaceWithWasm: function() {
            let player = this.game.getPlayer(this.userPlayerId);
            player.isComputer = true;
            player.type = "wasm";
        },
        addPlayer: function(apiResponse) {
            this.userPlayerId = parseInt(apiResponse.data);
            this.api.playerId = this.userPlayerId;
            if (this.useStorage()) {
                sessionStorage.playerId = this.userPlayerId;
            }
        },
        useApi: function() {
            return process.env.NODE_ENV !== "development" && this.shouldUseApi;
        },
        useStorage: function() {
            return process.env.NODE_ENV === "production";
        }
    },
    created: function() {
        if (!this.useApi()) {
            let gameFactory = this.gameFactory;
            if (gameFactory === null) {
                gameFactory = new GameFactory();
            }
            this.game = gameFactory.createGame();
            this.userPlayerId = this.game.getPlayers()[0].id;
        } else {
            if (this.useStorage() && sessionStorage.playerId) {
                this.userPlayerId = parseInt(sessionStorage.playerId);
                this.api.playerId = this.userPlayerId;
                this.api
                    .fetchState()
                    .then(this.startPolling)
                    .catch(error => {
                        if (error.response.data.key === "PLAYER_NOT_IN_GAME") {
                            this.enterGame();
                        }
                    });
            } else {
                this.enterGame();
            }
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
