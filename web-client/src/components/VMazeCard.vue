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
            :playerIndex="player.playerIndex"
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
        },
        rotation: {
            type: Number,
            default: 0
        }
    },
    data() {
        return {
            rotationClass: "noRotation",
            timer: 0
        };
    },
    watch: {
        rotation: function(newValue) {
            clearTimeout(this.timer);
            this.rotationClass = "rotateTo" + newValue;
            this.timer = setTimeout(() => {
                this.rotationClass = "rotate" + newValue;
            }, 500);
        }
    },
    computed: {
        rotationTransform: function() {
            let rotation = "rotate(" + this.rotation + "deg)";
            return { transform: rotation, "transform-origin": "50px 50px" };
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
                var midpointCircleRadius =
                    this.cardSize / sizeToSmallPieceCircleRadiusRatio;
                var fullCircle = Math.PI * 2;
                var angles = [fullCircle / numPieces / 2];
                for (var i = 1; i < numPieces; i++) {
                    angles.push(angles[i - 1] + fullCircle / numPieces);
                }
                var centers = [];
                angles.forEach(angle =>
                    centers.push({
                        x:
                            Math.floor(midpointCircleRadius * Math.sin(angle)) +
                            this.cardSize / 2,
                        y:
                            Math.floor(midpointCircleRadius * Math.cos(angle)) +
                            this.cardSize / 2
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
    /* transition: all 0.1s; */
    &__outline {
        stroke: black;
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
                stroke: blue;
            }
        }
    }

    &__wall {
        fill: grey;
    }

    &__pathway {
        fill: white;
        stroke: white;
    }

    &.interaction {
        cursor: pointer;
    }

    &__group {
        /* transition: all 1s; */
        transform-origin: 50px 50px;
    }
}

.rotateTo90 {
    animation-duration: 0.5s;
    animation-name: rotate90;
}

.rotate90 {
    transform: rotate(90deg);
}

@keyframes rotate90 {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(90deg);
    }
}

.rotateTo180 {
    animation-duration: 0.5s;
    animation-name: rotate180;
}

.rotate180 {
    transform: rotate(180deg);
}

@keyframes rotate180 {
    from {
        transform: rotate(90deg);
    }

    to {
        transform: rotate(180deg);
    }
}

.rotateTo270 {
    animation-duration: 0.5s;
    animation-name: rotate270;
}

.rotate270 {
    transform: rotate(270deg);
}

@keyframes rotate270 {
    from {
        transform: rotate(180deg);
    }

    to {
        transform: rotate(270deg);
    }
}

.rotateTo0 {
    animation-duration: 0.5s;
    animation-name: rotate0;
}

.rotate0 {
    transform: rotate(0deg);
}

@keyframes rotate0 {
    from {
        transform: rotate(270deg);
    }

    to {
        transform: rotate(360deg);
    }
}
</style>
