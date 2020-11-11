<template>
    <svg
        :x="$ui.boardOffset - borderWidth"
        :y="$ui.boardOffset - borderWidth"
        :width="boardSize + 2 * borderWidth"
        :height="boardSize + 2 * borderWidth"
    >
        <g>
            <rect
                :width="boardSize + 2 * borderWidth"
                :height="boardSize + 2 * borderWidth"
                class="game-board__background"
            ></rect>
            <transition-group name="game-board__maze-card-" tag="g">
                <v-maze-card
                    v-for="mazeCard in mazeCards"
                    @click.native="onMazeCardClick($event, mazeCard)"
                    :maze-card="mazeCard"
                    :key="'mazeCard-' + mazeCard.id"
                    :xPos="xPos(mazeCard)"
                    :yPos="yPos(mazeCard)"
                    :moveInteraction="isMoveInteractive(mazeCard)"
                    :shiftInteraction="isShiftInteractive(mazeCard)"
                    :reachable-by-player="reachableByPlayer(mazeCard)"
                    class="game-board__maze-card"
                ></v-maze-card>
            </transition-group>
        </g>
    </svg>
</template>

<script>
import VMazeCard from "@/components/VMazeCard.vue";
import { MOVE_ACTION, SHIFT_ACTION, NO_ACTION } from "@/model/game.js";

export default {
    name: "v-game-board",
    components: {
        /* eslint-disable vue/no-unused-components */
        VMazeCard
    },
    props: {
        mazeSize: {
            type: Number,
            required: true
        },
        mazeCards: {
            type: Array,
            required: true
        },
        interactiveMazeCards: {
            required: false,
            default: () => new Set()
        },
        requiredAction: {
            required: false,
            default: NO_ACTION
        },
        reachableCards: {
            required: false,
            default: () => new Set()
        },
        currentPlayerColor: {
            required: false,
            default: null
        },
        drag: {
            required: false,
            default: function() {
                return { row: false, column: false, offset: 0 };
            }
        }
    },
    computed: {
        boardSize: function() {
            return this.$ui.cardSize * this.mazeSize;
        },
        borderWidth: function() {
            return Math.floor(this.$ui.cardSize / 6);
        }
    },
    methods: {
        isMoveInteractive(mazeCard) {
            if (this.requiredAction === MOVE_ACTION) {
                return this.interactiveMazeCards.has(mazeCard);
            }
            return false;
        },
        isShiftInteractive(mazeCard) {
            if (this.requiredAction === SHIFT_ACTION) {
                return this.interactiveMazeCards.has(mazeCard);
            }
            return false;
        },
        reachableByPlayer(mazeCard) {
            if (this.currentPlayerColor !== null && this.reachableCards.has(mazeCard)) {
                return this.currentPlayerColor;
            }
            return null;
        },
        xPos(mazeCard) {
            let xPos = this.$ui.cardSize * mazeCard.location.column + this.borderWidth;
            if (this.drag.row === mazeCard.location.row) {
                xPos += this.drag.offset;
            }
            return xPos;
        },
        yPos(mazeCard) {
            let yPos = this.$ui.cardSize * mazeCard.location.row + this.borderWidth;
            if (this.drag.column === mazeCard.location.column) {
                yPos += this.drag.offset;
            }
            return yPos;
        },
        onMazeCardClick: function($event, mazeCard) {
            this.$emit("player-move", mazeCard);
        }
    }
};
</script>

<style lang="scss">
.game-board {
    &__background {
        fill: $color-game-board;
    }

    &__maze-card {
        &--enter-active,
        &--leave-active {
            transition: opacity 2s;
        }

        &--enter,
        &--leave-to {
            opacity: 0;
        }
    }
}
</style>
