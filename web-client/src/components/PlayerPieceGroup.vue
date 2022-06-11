<template>
    <g>
        <v-player-piece
            v-for="(player, index) in players"
            :x="pieceOrigins[index].x"
            :y="pieceOrigins[index].y"
            :key="'piece-' + player.id"
            :player="player"
            :interaction="playerTurns[index]"
            :width="pieceSizes[index]"
            :height="pieceSizes[index]"
        />
    </g>
</template>

<script>
import VPlayerPiece from "@/components/VPlayerPiece.vue";
import * as action from "@/model/player.js";

const smallPieceSizeFactor = 0.7;
const smallPieceCircleRadiusFactor = 0.5;

export default {
    name: "player-piece-group",
    components: {
        VPlayerPiece,
    },
    props: {
        players: {
            type: Array,
            required: true,
        },
        midPoint: {
            type: Number,
            required: true,
        },
        maxSize: {
            type: Number,
            required: true,
        },
    },
    computed: {
        playerTurns: function () {
            return this.players.map((player) => this.isTurn(player));
        },
        pieceSizes: function () {
            const pieceSize =
                this.players.length === 1 ? this.maxSize : this.maxSize * smallPieceSizeFactor;
            const turnFactor = 1.1;
            return this.players
                .map((player) => (this.isTurn(player) ? pieceSize * turnFactor : pieceSize))
                .map((size) => Math.floor(size));
        },
        pieceOrigins: function () {
            return this.pieceCenters.map((center, index) => ({
                x: center.x - this.pieceSizes[index] / 2,
                y: center.y - this.pieceSizes[index] / 2,
            }));
        },
        pieceCenters: function () {
            var numPieces = this.players.length;
            if (numPieces <= 1) {
                return [
                    {
                        x: Math.floor(this.midPoint),
                        y: Math.floor(this.midPoint),
                    },
                ];
            } else {
                var circleRadius = this.maxSize * smallPieceCircleRadiusFactor;
                var fullCircle = Math.PI * 2;
                var angles = [fullCircle / numPieces / 2];
                for (var i = 1; i < numPieces; i++) {
                    angles.push(angles[i - 1] + fullCircle / numPieces);
                }
                var centers = [];
                angles.forEach((angle) =>
                    centers.push({
                        x: Math.floor(circleRadius * Math.sin(angle)) + this.midPoint,
                        y: Math.floor(circleRadius * Math.cos(angle)) + this.midPoint,
                    })
                );
                return centers;
            }
        },
    },
    methods: {
        isTurn: function (player) {
            return player.nextAction !== action.NO_ACTION;
        },
    },
};
</script>
