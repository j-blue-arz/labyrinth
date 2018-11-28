<template>
    <svg :height="cardSize" :width="cardSize" :id="mazeCard.id" viewBox="0 0 100 100" class="maze-card">
        <rect x="0" y="0" :ry="edgeRadius" :height="cardSize" :width="cardSize" class="maze-card__wall maze-card__outline" />
        <rect :x="remainingSpace" :y="remainingSpace" :height="pathWidth" :width="pathWidth" class="maze-card__pathway" />
        <rect ref="northDoor" v-if="hasNorth"
            :x="remainingSpace" y="1" :height="remainingSpace" :width="pathWidth" class="maze-card__pathway" />
        <rect ref="eastDoor" v-if="hasEast"
            :x="(cardSize - 1) - (remainingSpace + 1)" :y="remainingSpace" :height="pathWidth" :width="remainingSpace + 1" class="maze-card__pathway" />
        <rect ref="southDoor" v-if="hasSouth"
            :x="remainingSpace" :y="(cardSize - 1) - (remainingSpace + 1)" :height="remainingSpace + 1" :width="pathWidth" class="maze-card__pathway" />
        <rect ref="westDoor" v-if="hasWest"
            x="1" :y="remainingSpace" :height="pathWidth" :width="remainingSpace" class="maze-card__pathway" />
        <v-player-piece
            v-for="(player, index) in players"
            :xCenterPos="pieceCenters[index].x"
            :yCenterPos="pieceCenters[index].y"
            :maxSize="pieceSize"
            :key="player.id"
            :playerPiece="player"
            />
    </svg>
</template>

<script>
import MazeCard from "@/model/mazecard.js";
import VPlayerPiece from "@/components/VPlayerPiece.vue";

const sizeToPathWidthRatio = 2.7;
const sizeToEdgeRadiusRatio = 7;
const sizeToPieceSizeRatio = 3.5;
const sizeToSmallPieceSizeRatio = 5;
const sizeToSmallPieceCircleRadiusRatio = 6;

export default {
    name: "v-maze-card",
    components: {
        /* eslint-disable vue/no-unused-components */
        VPlayerPiece
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
        return {};
    },
    computed: {
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
    &__outline {
        stroke: black;
    }

    &__wall {
        fill: grey;
    }

    &__pathway {
        fill: white;
        stroke: white;
    }
}
</style>
