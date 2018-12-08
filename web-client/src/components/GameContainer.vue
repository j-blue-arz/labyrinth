<template>
    <div class="game-container">
        <interactive-board
            @move-piece="onMovePlayerPiece"
            @insert-card="onInsertCard"
            :n="boardSize"
            :maze-cards="mazeCardsList"
            :card-size="cardSize"
            ref="interactive-board"
        />
        <v-maze-card
            @click.native="onLeftoverClick"
            v-if="hasStarted"
            :maze-card="leftoverMazeCard"
            :card-size="cardSize"
            class="game-container__leftover"
            ref="leftover"
        />
    </div>
</template>


<script>
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import VMazeCard from "@/components/VMazeCard.vue";
import Game from "@/model/game.js";
import GameFactory from "@/model/gameFactory.js";
import GameApi from "@/api/gameApi.js";
import MazeCard from "@/model/mazecard.js";
import * as player from "@/model/player.js";
import { setInterval, clearInterval } from "timers";

export default {
    name: "game-container",
    components: {
        InteractiveBoard,
        VMazeCard
    },
    props: {
        gameFactory: {
            type: GameFactory,
            required: false,
            default: null
        },
        api: {
            type: GameApi,
            required: false,
            default: () => new GameApi(location.protocol + "//" + location.host)
        }
    },
    data() {
        return {
            game: new Game(),
            cardSize: 100,
            playerId: 0,
            timer: 0
        };
    },
    computed: {
        mazeCardsList: function() {
            return this.game.mazeCardsAsList();
        },
        hasStarted: function() {
            return this.game.leftoverMazeCard instanceof MazeCard;
        },
        leftoverMazeCard: function() {
            return this.game.leftoverMazeCard;
        },
        boardSize: function() {
            return this.game.n;
        }
    },
    methods: {
        onInsertCard: function(location) {
            this.stopPolling();
            var rotation = this.game.leftoverMazeCard.rotation;
            if (process.env.NODE_ENV === "production") {
                this.api
                    .doShift(location, rotation)
                    .then(() => this.game.shift(location))
                    .catch(this.handleError)
                    .then(this.startPolling);
            } else {
                this.game.shift(location);
            }
        },
        onLeftoverClick: function() {
            if (this.getSelfPlayer().nextAction === player.SHIFT_ACTION) {
                this.game.leftoverMazeCard.rotateClockwise();
            }
        },
        onMovePlayerPiece: function(targetLocation) {
            this.stopPolling();
            if (process.env.NODE_ENV === "production") {
                this.api
                    .doMove(targetLocation)
                    .then(() => this.game.move(this.playerId, targetLocation))
                    .catch(this.handleError)
                    .then(this.startPolling);
            } else {
                this.game.move(this.playerId, targetLocation);
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
            if (this.timer === 0 && process.env.NODE_ENV === "production") {
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
        },
        addPlayer: function(apiResponse) {
            this.playerId = parseInt(apiResponse.data);
            this.api.playerId = this.playerId;
            sessionStorage.playerId = this.playerId;
        },
        getSelfPlayer: function() {
            return this.game.getPlayer(this.playerId);
        }
    },
    created: function() {
        if (process.env.NODE_ENV !== "production") {
            let gameFactory = this.gameFactory;
            if (gameFactory === null) {
                gameFactory = new GameFactory();
            }
            this.game = gameFactory.createGame();
        } else {
            if (sessionStorage.playerId) {
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

    &__leftover {
        top: 100px;
        cursor: pointer;
    }
}
</style>
