<template>
    <div class="game">
        <div class="game__board">
            <interactive-board v-if="hasStarted" :controller="controller" ref="interactive-board" />
        </div>
        <timer
            class="game__timer"
            :controller="controller"
            :countdown="countdown"
            :user-player="userPlayer"
        />
        <div class="game__score">
            <score-board :players="players" />
        </div>
        <div class="game__message">
            <v-message-area :countdown="countdown" :user-player="userPlayer" />
        </div>
        <leftover-maze-card
            class="game__leftover"
            :maze-card="leftoverMazeCard"
            :interaction="isMyTurnToShift"
            :style="{ width: leftoverSize, height: leftoverSize }"
        ></leftover-maze-card>
    </div>
</template>

<script>
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import ScoreBoard from "@/components/ScoreBoard.vue";
import Timer from "@/components/Timer.vue";
import VMessageArea from "@/components/VMessageArea.vue";
import LeftoverMazeCard from "@/components/LeftoverMazeCard.vue";
import * as action from "@/model/player.js";

export default {
    name: "v-game",
    components: {
        InteractiveBoard,
        ScoreBoard,
        Timer,
        VMessageArea,
        LeftoverMazeCard
    },
    props: {
        controller: {
            type: Object,
            required: true
        }
    },
    computed: {
        players: function() {
            return this.controller.game.getPlayers();
        },
        hasStarted: function() {
            return this.controller && this.controller.game && this.controller.game.hasStarted();
        },
        game: function() {
            return this.controller.game;
        },
        userPlayerId: function() {
            return this.controller.playerManager.getUserPlayerId();
        },
        userPlayer: function() {
            return this.controller.game.getPlayer(this.userPlayerId);
        },
        countdown: function() {
            return this.controller.turnCountdown;
        },
        isMyTurnToShift: function() {
            return (
                this.game.nextAction.playerId === this.userPlayerId &&
                this.game.nextAction.action === action.SHIFT_ACTION
            );
        },
        leftoverMazeCard: function() {
            return this.game.leftoverMazeCard;
        },
        leftoverSize: function() {
            let gameSize = this.game.n;
            return Math.round(100 / (gameSize + 2)) + "vmin";
        }
    }
};
</script>

<style lang="scss">
.game {
    z-index: 0;
    display: grid;

    --timer-height: 4rem;

    @media (orientation: landscape) {
        --gap: 2vh;

        grid-template-columns: minmax(70vh, 100vh) $game-widget-width;
        grid-template-rows:
            0 1fr var(--timer-height) var(--gap) calc(4 * var(--score-row-height)) var(--gap)
            auto 1fr;
        column-gap: var(--gap);
        grid-template-areas:
            "board leftover"
            "board ."
            "board timer"
            "board ."
            "board score"
            "board ."
            "board message"
            "board .";
    }

    @media (orientation: portrait) {
        grid-template-columns: 1fr 2fr 1fr;
        grid-template-rows:
            var(--timer-height) minmax(70vw, 100vw) calc(2 * var(--score-row-height))
            1fr;
        grid-template-areas:
            ". timer leftover"
            "board board board"
            "score score score"
            "message message message";
        gap: 1vw;
    }

    &__board {
        grid-area: board;
        position: relative;
        display: block;
        height: 0;
        padding-bottom: 100%;
        width: 100%;
    }

    &__timer {
        grid-area: timer;
        @include game-widget;
    }

    &__score {
        grid-area: score;
        @include game-widget;
    }

    &__message {
        grid-area: message;
    }

    &__leftover {
        grid-area: leftover;

        @media (orientation: landscape) {
            transform: translate(calc(-100% - var(--gap) / 2), 50%);
        }
    }
}
</style>
