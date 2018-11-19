<template>
    <svg
        :viewBox="`0 0 ${interactionSize} ${interactionSize}`"
        class="interactive-board">
        <v-game-board
            @maze-card-clicked="onMazeCardClick"
            :board-offset="boardOffset"
            :n="n"
            :maze-cards="mazeCards"
            :card-size="cardSize" />
        <rect
            v-for="(insertLocation, itemIndex) in insertLocations"
            @click="onInsertLocationClick($event, itemIndex)"
            :key="insertLocation.id"
            :x="xPos(insertLocation) + boardOffset"
            :y="yPos(insertLocation) + boardOffset"
            :height="cardSize"
            :width="cardSize"
            class="interactive-board__insert-location" />
    </svg>
</template>

<script>
import VGameBoard from "@/components/VGameBoard.vue";

export default {
    name: "interactive-board",
    components: {
        /* eslint-disable vue/no-unused-components */
        VGameBoard
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
        cardSize: {
            type: Number,
            required: true
        }
    },
    data() {
        return {
            insertLocations: [
                { id: 0, row: -1, column: 1 },
                { id: 1, row: -1, column: 3 },
                { id: 2, row: -1, column: 5 },
                { id: 3, row: this.n, column: 1 },
                { id: 4, row: this.n, column: 3 },
                { id: 5, row: this.n, column: 5 },
                { id: 6, row: 1, column: -1 },
                { id: 7, row: 3, column: -1 },
                { id: 8, row: 5, column: -1 },
                { id: 9, row: 1, column: this.n },
                { id: 10, row: 3, column: this.n },
                { id: 11, row: 5, column: this.n }
            ]
        };
    },
    computed: {
        interactionSize: function() {
            return this.cardSize * (this.n + 2);
        },
        boardOffset: function() {
            return this.cardSize;
        }
    },
    methods: {
        xPos(location) {
            return this.cardSize * location.column;
        },
        yPos(location) {
            return this.cardSize * location.row;
        },
        onInsertLocationClick: function(event, itemIndex) {
            var insertLocation = this.insertLocations[itemIndex];
            this.$emit("insert-card", insertLocation);
        },
        onMazeCardClick: function(mazeCard) {
            this.$emit("move-piece", mazeCard.location);
        }
    }
};
</script>

<style lang="scss">
.interactive-board {
    top: 0;
    left: 0;
    max-height: 100%;
    max-width: 100%;
    width: 900px;

    &__insert-location {
        opacity: 0.1;
        cursor: pointer;
    }
}

.game-board {
    &__background {
        fill: lightblue;
    }
}
.game-board-move {
    transition: transform 0.5s ease-in-out;
}
</style>
