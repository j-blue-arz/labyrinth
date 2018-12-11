<template>
    <div class="game-container">
        <interactive-board
            @move-piece="onMovePlayerPiece"
            @insert-card="onInsertCard"
            :game="game"
            :card-size="cardSize"
            :player-id="playerId"
            ref="interactive-board"
        />
    </div>
</template>


<script>
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import Game, * as actions from "@/model/game.js";
import GameFactory from "@/model/gameFactory.js";
import GameApi from "@/api/gameApi.js";
import { setInterval, clearInterval } from "timers";

export default {
    name: "game-container",
    components: {
        InteractiveBoard
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
            playerId: 0,
            timer: 0,
            api: new GameApi(location.protocol + "//" + location.host)
        };
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
            }
        },
        onMovePlayerPiece: function(targetLocation) {
            this.stopPolling();
            if (this.useApi()) {
                this.api
                    .doMove(targetLocation)
                    .then(() => this.game.move(this.playerId, targetLocation))
                    .catch(this.handleError)
                    .then(this.startPolling);
            } else {
                this.game.move(this.playerId, targetLocation);
                this.game.nextAction.action = actions.SHIFT_ACTION;
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
            this.game.createFromApi(apiResponse.data);
            //this.$forceUpdate();
        },
        addPlayer: function(apiResponse) {
            this.playerId = parseInt(apiResponse.data);
            this.api.playerId = this.playerId;
            if (this.useStorage()) {
                sessionStorage.playerId = this.playerId;
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
                this.playerId = parseInt(sessionStorage.playerId);
                this.api.playerId = this.playerId;
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
