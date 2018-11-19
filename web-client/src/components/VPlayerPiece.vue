<template>
    <circle
        :cx="xCenterPos"
        :cy="yCenterPos"
        :r="maxSize/2"
        :fill="playerColor"
        class="player-piece"/>
</template>

<script>
import { hasPropertyWithType } from "@/util/validation.js";

export default {
    name: "v-player-piece",
    props: {
        playerPiece: {
            type: Object,
            required: true,
            validator: function(obj) {
                return (
                    hasPropertyWithType(obj, "id", "number") &&
                    Number.isInteger(obj.id)
                );
            }
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
