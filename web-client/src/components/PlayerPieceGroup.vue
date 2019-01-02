<template>
    <g>
        <v-player-piece
            v-for="(player, index) in players"
            :xCenterPos="pieceCenters[index].x"
            :yCenterPos="pieceCenters[index].y"
            :maxSize="pieceSize"
            :key="'piece-' + player.id"
            :player="player"
        />
    </g>
</template>

<script>
import VPlayerPiece from "@/components/VPlayerPiece.vue";

const smallPieceSizeFactor = 0.7;
const smallPieceCircleRadiusFactor = 0.6;

export default {
    name: "player-piece-group",
    components: {
        VPlayerPiece
    },
    props: {
        players: {
            type: Array,
            required: true
        },
        midPoint: {
            type: Number,
            required: true
        },
        maxSize: {
            type: Number,
            required: true
        }
    },
    computed: {
        pieceSize: function() {
            if (this.players.length === 1) {
                return Math.floor(this.maxSize);
            } else {
                return Math.floor(this.maxSize * smallPieceSizeFactor);
            }
        },
        pieceCenters: function() {
            var numPieces = this.players.length;
            if (numPieces <= 1) {
                return [
                    {
                        x: Math.floor(this.midPoint),
                        y: Math.floor(this.midPoint)
                    }
                ];
            } else {
                var circleRadius = this.maxSize * smallPieceCircleRadiusFactor;
                var fullCircle = Math.PI * 2;
                var angles = [fullCircle / numPieces / 2];
                for (var i = 1; i < numPieces; i++) {
                    angles.push(angles[i - 1] + fullCircle / numPieces);
                }
                var centers = [];
                angles.forEach(angle =>
                    centers.push({
                        x: Math.floor(circleRadius * Math.sin(angle)) + this.midPoint,
                        y: Math.floor(circleRadius * Math.cos(angle)) + this.midPoint
                    })
                );
                return centers;
            }
        }
    }
};
</script>
