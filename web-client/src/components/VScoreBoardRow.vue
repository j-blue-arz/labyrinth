<template>
    <tr class="score-row" :class="colorIndexClass">
        <td class="score-row__current-player">
            <span
                :v-if="isTurn"
                class="score-row__current-player--marker"></span>
        </td>
        <td class="score-row__player-piece">
            <v-player-piece
                :xCenterPos="15"
                :yCenterPos="15"
                :maxSize="25"
                :player="player"
                :svgSize="30"
                class="score-row__piece-symbol"
            />
        </td>
        <td class="score-row__player-name">{{playerName}}</td>
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
        },
        playerName: function() {
            if (this.player.isUser) {
                return "You";
            } else if (!this.player.isComputer) {
                return "";
            } else {
                return this.player.algorithm;
            }
        },
        isTurn: function() {
            return this.player.hasToMove() || this.player.hasToShift();
        }
    }
};
</script>

<style lang="scss">
.score-row {
    height: 40px;

    &--player-0 td:not(&__current-player) {
        background: $color-player-0-secondary;
    }

    &--player-1 td:not(&__current-player) {
        background: $color-player-1-secondary;
    }

    &--player-2 td:not(&__current-player) {
        background: $color-player-2-secondary;
    }

    &--player-3 td:not(&__current-player) {
        background: $color-player-3-secondary;
    }

    &__current-player {
        position: relative;
    }

    &__current-player--marker {
        border: 10px solid $interaction-color;
        border-radius: 50%;
        display: inline-block;
    }

    &__player-piece {
        width: 4rem;
        text-align: center;
    }

    &__piece-symbol {
        display: block;
        margin: auto;
    }

    &__player-name {
        width: 4rem;
    }

    &__score-data {
        border-left: 1px solid $color-table-border;
        text-align: right;
        padding-right: 8px;
        width: 2rem;
    }
}
</style>
