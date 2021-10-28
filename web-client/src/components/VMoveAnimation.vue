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
import Graph from "@/model/Graph.js";

export default {
    name: "v-move-animation",
    props: {
        player: {
            required: true
        }
    },
    data() {
        return {
            isAnimating: false,
            path: []
        };
    },
    watch: {
        mazeCardId: function(newMazeCardId, oldMazeCardId) {
            const newMazeCard = this.$store.getters["board/mazeCardById"](newMazeCardId);
            const oldMazeCard = this.$store.getters["board/mazeCardById"](oldMazeCardId);
            if (newMazeCard && oldMazeCard) {
                if (!this.isLeftover(newMazeCard) && !this.isLeftover(oldMazeCard)) {
                    let sourceLocation = oldMazeCard.location;
                    let targetLocation = newMazeCard.location;
                    let graph = new Graph(this.$store.state.board);
                    let locations = graph.path(sourceLocation, targetLocation);
                    this.path = locations.map(location => this.locationToPosition(location));
                    this.correctLastSegment();
                    this.animatePath();
                }
            }
        }
    },
    computed: {
        mazeCardId: function() {
            return this.player.mazeCard;
        },
        colorIndexClass: function() {
            return "move-animation__path--player-" + this.player.pieceIndex;
        }
    },
    methods: {
        animatePath: function() {
            this.isAnimating = true;
            setTimeout(() => {
                this.isAnimating = false;
            }, 1400);
        },
        correctLastSegment: function() {
            if (this.path.length > 1) {
                let lastSegment = this.path[this.path.length - 1];
                let secondLastSegment = this.path[this.path.length - 2];
                lastSegment[0] = (3 * lastSegment[0] + secondLastSegment[0]) / 4;
                lastSegment[1] = (3 * lastSegment[1] + secondLastSegment[1]) / 4;
            }
        },
        locationToPosition: function(location) {
            let offset = this.$ui.cardSize / 2;
            let x = location.column * this.$ui.cardSize + offset;
            let y = location.row * this.$ui.cardSize + offset;
            return [x, y];
        },
        isLeftover: function(mazeCard) {
            return mazeCard.id === this.$store.state.board.leftoverId || !mazeCard.location;
        }
    }
};
</script>

<style lang="scss">
@mixin move-animation__path--final {
    opacity: 0.85;
    stroke-width: 9;
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
