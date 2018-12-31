<template>
    <svg
        :x="boardOffset - borderWidth"
        :y="boardOffset - borderWidth"
        :width="boardSize + 2*borderWidth"
        :height="boardSize + 2*borderWidth"
    >
        <rect
            :width="boardSize + 2*borderWidth"
            :height="boardSize + 2*borderWidth"
            class="game-board__background"
        ></rect>
        <transition-group name="game-board__maze-card-" tag="g">
            <v-maze-card
                v-for="mazeCard in mazeCards"
                @click.native="onMazeCardClick($event, mazeCard)"
                :maze-card="mazeCard"
                :key="mazeCard.id"
                :card-size="cardSize"
                :x="xPos(mazeCard.location) + borderWidth"
                :y="yPos(mazeCard.location) + borderWidth"
                :class="{interaction: isInteractive(mazeCard)}"
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
        cardSize: {
            type: Number,
            default: 100
        },
        boardOffset: {
            type: Number,
            default: 100
        },
        interactiveMazeCards: {
            required: false,
            default: false
        }
    },
    data() {
        return {};
    },
    computed: {
        boardSize: function() {
            return this.cardSize * this.n;
        },
        borderWidth: function() {
            return Math.floor(this.cardSize / 6);
        }
    },
    methods: {
        interactiveMazeCardSet() {
            if (this.interactiveMazeCards !== false) {
                return new Set(this.interactiveMazeCards);
            }
            return new Set([]);
        },
        isInteractive(mazeCard) {
            let interactiveSet = this.interactiveMazeCardSet();
            return interactiveSet.has(mazeCard);
        },
        xPos(location) {
            return this.cardSize * location.column;
        },
        yPos(location) {
            return this.cardSize * location.row;
        },
        onMazeCardClick: function($event, mazeCard) {
            this.$emit("maze-card-clicked", mazeCard);
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
        &--move {
            transition: transform 10s;
        }

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
