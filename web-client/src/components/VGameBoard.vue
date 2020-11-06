<template>
    <svg
        :x="$ui.boardOffset - borderWidth"
        :y="$ui.boardOffset - borderWidth"
        :width="boardSize + 2 * borderWidth"
        :height="boardSize + 2 * borderWidth"
        @mousedown="startDrag($event)"
        @mousemove="drag($event)"
        @mouseup="endDrag($event)"
        @mouseleave="endDrag($event)"
    >
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
                :interaction="isInteractive(mazeCard)"
                :reachable-by-player="reachableByPlayer(mazeCard)"
                class="game-board__maze-card"
            ></v-maze-card>
        </transition-group>
    </svg>
</template>

<script>
import VMazeCard from "@/components/VMazeCard.vue";

export default {
    name: "v-game-board",
    components: {
        /* eslint-disable vue/no-unused-components */
        VMazeCard
    },
    props: {
        n: {
            type: Number,
            default: 7,
            validator: function(num) {
                return num % 2 == 1;
            }
        },
        mazeCards: {
            type: Array,
            required: true
        },
        interactiveMazeCards: {
            required: false,
            default: () => new Set([])
        },
        reachableCards: {
            required: false,
            default: () => new Set([])
        },
        currentPlayerColor: {
            required: false,
            default: null
        }
    },
    data() {
        return {
            draggedMazeCardId: null,
            dragStart: null,
            dragOffset: null
        };
    },
    computed: {
        boardSize: function() {
            return this.$ui.cardSize * this.n;
        },
        borderWidth: function() {
            return Math.floor(this.$ui.cardSize / 6);
        }
    },
    methods: {
        isInteractive(mazeCard) {
            return this.interactiveMazeCards.has(mazeCard);
        },
        reachableByPlayer(mazeCard) {
            if (this.currentPlayerColor !== null && this.reachableCards.has(mazeCard)) {
                return this.currentPlayerColor;
            }
            return null;
        },
        xPos(mazeCard) {
            let xPos = this.$ui.cardSize * mazeCard.location.column + this.borderWidth;
            if (mazeCard.id === this.draggedMazeCardId) {
                xPos += this.dragOffset.x;
            }
            return xPos;
        },
        yPos(mazeCard) {
            let yPos = this.$ui.cardSize * mazeCard.location.row + this.borderWidth;
            if (mazeCard.id === this.draggedMazeCardId) {
                yPos += this.dragOffset.y;
            }
            return yPos;
        },
        onMazeCardClick: function($event, mazeCard) {
            this.$emit("maze-card-clicked", mazeCard);
        },
        startDrag: function($event) {
            let mousePosition = this.getMousePosition($event);
            let mazeCard = this.getMazeCard(mousePosition);
            if (mazeCard) {
                this.draggedMazeCardId = mazeCard.id;
                this.dragStart = mousePosition;
            }
            this.dragOffset = { x: 0, y: 0 };
        },
        drag: function($event) {
            if (this.draggedMazeCardId !== null) {
                $event.preventDefault();
                let mousePosition = this.getMousePosition($event);
                this.dragOffset = this.offset(this.dragStart, mousePosition);
            }
        },
        endDrag: function($event) {
            this.draggedMazeCardId = null;
            this.dragStart = null;
            this.dragOffset = { x: 0, y: 0 };
        },
        offset: function(from, to) {
            return {
                x: to.x - from.x,
                y: to.y - from.y
            };
        },
        getMousePosition(evt) {
            const svg = evt.currentTarget;
            const CTM = svg.getScreenCTM();
            return {
                x: (evt.clientX - CTM.e) / CTM.a,
                y: (evt.clientY - CTM.f) / CTM.d
            };
        },
        getMazeCard(mousePosition) {
            let column = Math.floor((mousePosition.x - this.$ui.boardOffset) / this.$ui.cardSize);
            let row = Math.floor((mousePosition.y - this.$ui.boardOffset) / this.$ui.cardSize);
            let mazeCard = this.mazeCards.find(
                mazeCard => mazeCard.location.row == row && mazeCard.location.column == column
            );
            return mazeCard;
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
