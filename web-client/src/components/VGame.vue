<template>
    <div class="game">
        <div class="game__board">
            <interactive-board v-if="hasBoard" ref="interactive-board" />
        </div>
        <countdown-timer class="game__timer" />
        <div class="game__score">
            <score-board />
        </div>
        <div class="game__message">
            <v-message-area />
        </div>
        <leftover-maze-card
            class="game__leftover"
            v-if="hasBoard"
            :style="{ width: leftoverSize, height: leftoverSize }"
        ></leftover-maze-card>
    </div>
</template>

<script>
import InteractiveBoard from "@/components/InteractiveBoard.vue";
import ScoreBoard from "@/components/ScoreBoard.vue";
import CountdownTimer from "@/components/CountdownTimer.vue";
import VMessageArea from "@/components/VMessageArea.vue";
import LeftoverMazeCard from "@/components/LeftoverMazeCard.vue";

import { mapState } from "pinia";
import { useBoardStore } from "@/stores/board.js";
import { usePlayersStore } from "@/stores/players.js";

export default {
    name: "v-game",
    components: {
        InteractiveBoard,
        ScoreBoard,
        CountdownTimer,
        VMessageArea,
        LeftoverMazeCard,
    },
    computed: {
        ...mapState(usePlayersStore, ["userPlayer"]),
        ...mapState(useBoardStore, {
            hasBoard: (store) => store.notEmpty,
            leftoverSize: (store) => {
                return Math.round(100 / (store.mazeSize + 2)) + "vmin";
            },
        }),
    },
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
            0 1fr var(--timer-height) var(--gap) calc(4 * var(--score-row-height) + 1px) var(--gap)
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
            var(--timer-height) minmax(70vw, 100vw) calc(2 * var(--score-row-height) + 1px)
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
            transform: translate(0px, 50%);
        }

        @media (orientation: portrait) {
            place-self: center;
            transform: translateY(15%);
        }
    }
}
</style>
