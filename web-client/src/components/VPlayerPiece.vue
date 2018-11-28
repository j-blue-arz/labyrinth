<template>
    <circle
        :cx="xCenterPos"
        :cy="yCenterPos"
        :r="maxSize/2"
        :fill="playerColor"
        class="player-piece"/>
</template>

<script>
import Player from "@/model/player.js";

export default {
    name: "v-player-piece",
    props: {
        playerPiece: {
            type: Player,
            required: true
        },
        xCenterPos: {
            type: Number,
            require: true
        },
        yCenterPos: {
            type: Number,
            require: true
        },
        maxSize: {
            type: Number,
            require: true
        }
    },
    data() {
        return {
            playerColors: ["yellow", "lightblue", "darkgreen", "black"]
        };
    },
    computed: {
        playerColor: function() {
            return this.playerColors[
                this.playerPiece.id % this.playerColors.length
            ];
        }
    }
};
</script>

<style lang="scss">
.player-piece {
    stroke: black;
    stroke-width: 3px;
}
</style>
