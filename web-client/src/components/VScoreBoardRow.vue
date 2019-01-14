<template>
    <tr class="score-row" :class="colorIndexClass">
        <td class="score-row__player-data">
            <v-player-piece
                :xCenterPos="15"
                :yCenterPos="15"
                :maxSize="25"
                :player="player"
                :svgSize="30"
                class="score-row__player-piece"
            />
        </td>
        <td class="score-row__score-data">{{player.score}}</td>
    </tr>
</template>

<script>
import VPlayerPiece from "@/components/VPlayerPiece.vue";
import Player from "@/model/player.js";

export default {
    name: "v-score-board-row",
    components: {
        VPlayerPiece
    },
    props: {
        player: {
            type: Player,
            required: true
        }
    },
    computed: {
        colorIndexClass: function() {
            return "score-row--player-" + this.player.colorIndex;
        }
    }
};
</script>

<style lang="scss">
.score-row {
    height: 40px;

    &--player-0 {
        background: $color-player-0-secondary;
    }

    &--player-1 {
        background: $color-player-1-secondary;
    }

    &--player-2 {
        background: $color-player-2-secondary;
    }

    &--player-3 {
        background: $color-player-3-secondary;
    }

    td {
        padding: 3px;
    }

    &__player-data {
        width: 40px;
        text-align: center;
    }

    &__player-piece {
        display: block;
        margin: auto;
    }

    &__score-data {
        border-left: 1px solid $color-table-border;
        text-align: right;
    }
}
</style>
