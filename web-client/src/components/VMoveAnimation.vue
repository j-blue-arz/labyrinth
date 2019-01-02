<template>
    <transition name="move-animation-">
        <path
            v-if="isAnimating"
            :d="`M${path}`"
            :class="colorIndexClass"
            class="move-animation__path"
            filter="url(#plasticity)"
        />
    </transition>
</template>

<script>
import Game from "@/model/game.js";
import Graph from "@/model/mazeAlgorithm.js";
import Player from "@/model/player.js";

export default {
    name: "v-move-animation",
    props: {
        game: {
            type: Game,
            required: true
        },
        player: {
            type: Player,
            required: true
        },
        cardSize: {
            type: Number,
            default: 100
        },
        boardOffset: {
            type: Number,
            default: 100
        }
    },
    data() {
        return {
            isAnimating: false,
            path: []
        };
    },
    watch: {
        mazeCard: function(newMazeCard, oldMazeCard) {
            if (newMazeCard && oldMazeCard) {
                if (!this.isLeftover(newMazeCard)) {
                    let sourceLocation = oldMazeCard.location;
                    let targetLocation = newMazeCard.location;
                    let graph = new Graph(this.game);
                    let locations = graph.path(sourceLocation, targetLocation);
                    this.path = locations.map(location => this.locationToPosition(location));
                    this.animatePath();
                }
            }
        }
    },
    computed: {
        mazeCard: function() {
            return this.player.mazeCard;
        },
        colorIndexClass: function() {
            return "move-animation__path--player-" + this.player.colorIndex;
        }
    },
    methods: {
        animatePath: function() {
            this.isAnimating = true;
            setTimeout(() => {
                this.isAnimating = false;
            }, 1400);
        },
        locationToPosition: function(location) {
            let cardMidpoint = this.cardSize / 2;
            let offset = cardMidpoint + this.boardOffset;
            let x = location.column * this.cardSize + offset;
            let y = location.row * this.cardSize + offset;
            return [x, y];
        },
        isLeftover: function(mazeCard) {
            return mazeCard.id === this.game.leftoverMazeCard.id || mazeCard.isLeftoverLocation();
        }
    }
};
</script>

<style lang="scss">
@mixin move-animation__path--final {
    opacity: 0.8;
    stroke-width: 8;
}
.move-animation {
    &__path {
        &--player-0 {
            stroke: $color-player-0;
        }

        &--player-1 {
            stroke: $color-player-1;
        }

        &--player-2 {
            stroke: $color-player-2;
        }

        &--player-3 {
            stroke: $color-player-3;
        }

        @include move-animation__path--final;
        stroke-linejoin: round;
        stroke-linecap: round;
        fill: none;
    }

    &--enter-active,
    &--leave-active {
        transition: all 0.4s ease-in-out;
    }

    &--enter,
    &--leave-to {
        stroke-width: 15;
        opacity: 0;
    }

    &--enter-to,
    &--leave {
        @include move-animation__path--final;
    }
}
</style>
