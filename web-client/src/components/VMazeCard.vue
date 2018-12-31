<template>
    <svg
        :height="cardSize"
        :width="cardSize"
        :id="mazeCard.id"
        viewBox="0 0 100 100"
        class="maze-card"
    >
        <g class="maze-card__group" :class="rotationClass">
            <rect
                x="0"
                y="0"
                :ry="edgeRadius"
                :height="cardSize"
                :width="cardSize"
                class="maze-card__wall maze-card__outline"
            ></rect>
            <rect
                :x="remainingSpace"
                :y="remainingSpace"
                :height="pathWidth"
                :width="pathWidth"
                class="maze-card__pathway"
            ></rect>
            <rect
                ref="northDoor"
                v-if="hasNorth"
                :x="remainingSpace"
                y="1"
                :height="remainingSpace"
                :width="pathWidth"
                class="maze-card__pathway"
            ></rect>
            <rect
                ref="eastDoor"
                v-if="hasEast"
                :x="(cardSize - 1) - (remainingSpace + 1)"
                :y="remainingSpace"
                :height="pathWidth"
                :width="remainingSpace + 1"
                class="maze-card__pathway"
            ></rect>
            <rect
                ref="southDoor"
                v-if="hasSouth"
                :x="remainingSpace"
                :y="(cardSize - 1) - (remainingSpace + 1)"
                :height="remainingSpace + 1"
                :width="pathWidth"
                class="maze-card__pathway"
            ></rect>
            <rect
                ref="westDoor"
                v-if="hasWest"
                x="1"
                :y="remainingSpace"
                :height="pathWidth"
                :width="remainingSpace"
                class="maze-card__pathway"
            ></rect>
        </g>
        <v-player-piece
            v-for="(player, index) in players"
            :xCenterPos="pieceCenters[index].x"
            :yCenterPos="pieceCenters[index].y"
            :maxSize="pieceSize"
            :key="player.id"
            :player="player"
        ></v-player-piece>
        <v-objective v-if="mazeCard.hasObject"></v-objective>
    </svg>
</template>

<script>
import MazeCard from "@/model/mazecard.js";
import VPlayerPiece from "@/components/VPlayerPiece.vue";
import VObjective from "@/components/VObjective.vue";

const sizeToPathWidthRatio = 2.7;
const sizeToEdgeRadiusRatio = 7;
const sizeToPieceSizeRatio = 3.5;
const sizeToSmallPieceSizeRatio = 5;
const sizeToSmallPieceCircleRadiusRatio = 6;

export default {
    name: "v-maze-card",
    components: {
        /* eslint-disable vue/no-unused-components */
        VPlayerPiece,
        VObjective
    },
    props: {
        mazeCard: {
            type: MazeCard,
            required: true
        },
        cardSize: {
            type: Number,
            default: 100
        }
    },
    data() {
        return {
            animatedRotationClass: "",
            timer: 0
        };
    },
    watch: {
        rotation: function(newValue) {
            clearTimeout(this.timer);
            this.animatedRotationClass = "rotateTo" + newValue;
            this.timer = setTimeout(() => {
                this.animatedRotationClass = "rotate" + newValue;
            }, 500);
        }
    },
    computed: {
        rotation: function() {
            return this.mazeCard.rotation;
        },
        rotationClass: function() {
            if (this.animatedRotationClass === "") {
                return "rotate" + this.mazeCard.rotation;
            }
            return this.animatedRotationClass;
        },
        players: function() {
            return this.mazeCard.players;
        },
        pieceSize: function() {
            if (this.players.length === 1) {
                return Math.floor(this.cardSize / sizeToPieceSizeRatio);
            } else {
                return Math.floor(this.cardSize / sizeToSmallPieceSizeRatio);
            }
        },
        pieceCenters: function() {
            var numPieces = this.mazeCard.players.length;
            if (numPieces <= 1) {
                return [
                    {
                        x: Math.floor(this.cardSize / 2),
                        y: Math.floor(this.cardSize / 2)
                    }
                ];
            } else {
                var midpointCircleRadius = this.cardSize / sizeToSmallPieceCircleRadiusRatio;
                var fullCircle = Math.PI * 2;
                var angles = [fullCircle / numPieces / 2];
                for (var i = 1; i < numPieces; i++) {
                    angles.push(angles[i - 1] + fullCircle / numPieces);
                }
                var centers = [];
                angles.forEach(angle =>
                    centers.push({
                        x: Math.floor(midpointCircleRadius * Math.sin(angle)) + this.cardSize / 2,
                        y: Math.floor(midpointCircleRadius * Math.cos(angle)) + this.cardSize / 2
                    })
                );
                return centers;
            }
        },
        pathWidth: function() {
            return Math.floor(this.cardSize / sizeToPathWidthRatio);
        },
        edgeRadius: function() {
            return Math.floor(this.cardSize / sizeToEdgeRadiusRatio);
        },
        remainingSpace: function() {
            return Math.floor((this.cardSize - this.pathWidth) / 2);
        },
        hasNorth: function() {
            return this.mazeCard.hasNorthDoor();
        },
        hasEast: function() {
            return this.mazeCard.hasEastDoor();
        },
        hasSouth: function() {
            return this.mazeCard.hasSouthDoor();
        },
        hasWest: function() {
            return this.mazeCard.hasWestDoor();
        }
    }
};
</script>

<style lang="scss">
.maze-card {
    &__outline {
        stroke: $color-outline;
        stroke-width: 1px;
        stroke-opacity: 0.8;
    }

    &.interaction {
        .maze-card__outline {
            stroke-width: 2px;
            stroke-opacity: 1;
        }

        &:hover {
            .maze-card__outline {
                stroke: $color-outline-active;
            }
        }
    }

    &__wall {
        fill: $color-walls;
    }

    &__pathway {
        fill: $color-pathways;
        stroke: $color-pathways;
    }

    &.interaction {
        cursor: pointer;
    }

    &__group {
        transform-origin: 50px 50px;
    }
}

$degrees: 0 90 180 270;
@each $rotation in $degrees {
    $to: $rotation;
    @if $rotation == 0 {
        $to: 360;
    }
    $from: $to - 90;
    $animationName: from#{$from}to#{$to};

    .rotateTo#{$rotation} {
        @include rotationAnimation($animationName);
    }

    .rotate#{$rotation} {
        transform: rotate($rotation + deg);
    }

    @include rotateFromTo($animationName, $from + deg, $to + deg);
}
</style>
