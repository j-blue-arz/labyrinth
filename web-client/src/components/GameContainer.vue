<template>
    <div class="game-container">
        <interactive-board
            @move-piece="onMovePlayerPiece"
            @insert-card="onInsertCard"
            :game="game"
            :card-size="cardSize"
            :user-player-id="userPlayerId"
            ref="interactive-board"
        />
        <game-menu
            v-if="isUsingApi"
            :api="api"
            :game="game"
            :user-player-id="userPlayerId"
            @called-api-method="startPolling"
        />
    </div>
</template>


<script>
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import GameMenu from "@/components/GameMenu.vue";
import Game, * as actions from "@/model/game.js";
import GameFactory from "@/model/gameFactory.js";
import GameApi from "@/api/gameApi.js";
import { setInterval, clearInterval } from "timers";

export default {
    name: "game-container",
    components: {
        InteractiveBoard,
        GameMenu
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
            cardSize: 100,
            userPlayerId: 0,
            timer: 0,
            api: new GameApi(location.protocol + "//" + location.host)
        };
    },
    computed: {
        isUsingApi: function() {
            return this.useApi();
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
        } else {
            if (this.useStorage() && sessionStorage.playerId) {
                this.userPlayerId = parseInt(sessionStorage.playerId);
                this.api.playerId = this.userPlayerId;
                this.api
                    .fetchState()
                    .catch(error => {
                        if (error.response.data.key === "PLAYER_NOT_IN_GAME") {
                            this.api
                                .doAddPlayer()
                                .then(this.addPlayer)
                                .catch(this.handleError);
                        }
                    })
                    .then(this.startPolling);
            } else {
                this.api
                    .doAddPlayer()
                    .then(this.addPlayer)
                    .catch(this.handleError)
                    .then(this.startPolling);
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
    width: 100%;
    height: 100%;
    position: relative;
    display: flex;
    flex-flow: row wrap;
}
</style>
