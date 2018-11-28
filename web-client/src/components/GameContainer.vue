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
import { setInterval } from "timers";

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
            timer: ""
        };
    },
    computed: {
        mazeCardsList: function() {
            return this.game.mazeCardsAsList();
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
            this.api.doShift(
                location,
                this.game.leftoverMazeCard.rotation,
                this.logError
            );
            this.game.shift(location);
        },
        onLeftoverClick: function() {
            this.game.leftoverMazeCard.rotateClockwise();
        },
        onMovePlayerPiece: function(targetLocation) {
            this.api.doMove(targetLocation, this.logError);
            this.game.move(this.playerId, targetLocation);
        },
        logError: function(errorResponseData) {
            console.error(errorResponseData);
        },
        fetchApiState: function() {
            this.api.fetchState(this.createGameFromApi, this.logError);
        },
        createGameFromApi: function(apiState) {
            this.game.createFromApi(apiState);
        },
        addPlayer: function(responseData) {
            console.log(responseData);
            this.playerId = parseInt(responseData);
            this.api.playerId = this.playerId;
        }
    },
    created: function() {
        if (this.gameFactory !== null) {
            this.game = this.gameFactory.createGame();
        } else {
            this.api.doAddPlayer(this.addPlayer, this.logError);
            this.timer = setInterval(this.fetchApiState, 800);
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
