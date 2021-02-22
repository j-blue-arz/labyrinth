<template>
    <div class="score-row" :class="[colorIndexClass, { 'score-row--is-turn': isTurn }]">
        <span v-if="isTurn" class="score-row__current-player--marker"></span>
        <v-player-piece
            :xCenterPos="15"
            :yCenterPos="15"
            :maxSize="25"
            :player="player"
            :svgSize="30"
            class="score-row__piece-symbol"
        />
        <div class="score-row__player-name">
            <p>{{ playerName }}</p>
        </div>
        <p class="score-row__score-data">{{ player.score }}</p>
    </div>
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
            return this.player.getLabel();
        },
        isTurn: function() {
            return this.player.hasToMove() || this.player.hasToShift();
        }
    }
};
</script>

<style lang="scss">
.score-row {
    height: var(--score-row-height);
    width: $game-widget-width;
    display: flex;
    flex-flow: row nowrap;
    align-items: center;
    justify-content: flex-end;
    border: 2px solid transparent;

    &--is-turn {
        border: 2px solid $interaction-color;
    }

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

    &__player-piece {
        width: 3rem;
        display: flex;
        align-items: center;
    }

    &__piece-symbol {
        width: 3rem;
    }

    &__player-name {
        --text-height: calc(var(--score-row-height) - 0.2rem);
        width: 8rem;
        line-height: calc(var(--text-height) / 3);
        height: var(--text-height);
        overflow: hidden;
        border-right: 1px solid $color-ui-border;

        & p {
            overflow: hidden;
            height: var(--text-height);
            vertical-align: middle;
            display: table-cell;
        }
    }

    &__score-data {
        text-align: right;
        padding-right: 0.5rem;
        width: 2rem;
    }
}
</style>
