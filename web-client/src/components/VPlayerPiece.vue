<template>
    <svg ref="playerPiece" class="player-piece" :class="colorIndexClass" viewBox="0 0 30 30">
        <circle
            cx="15"
            cy="15"
            r="12.5"
            class="player-piece__shape"
            :class="{ 'player-piece--is-user': isUser }"
            :filter="interaction ? 'url(#drop-shadow)' : ''"
        />
        <circle
            v-if="interaction && isUser"
            cx="15"
            cy="15"
            r="14.5"
            class="player-piece__halo"
        ></circle>
        <text
            x="15"
            y="15"
            textLength="12.5"
            font-size="22"
            class="player-piece__text"
            :class="{ 'player-piece--is-user': isUser }"
            dominant-baseline="central"
            text-anchor="middle"
        >
            {{ playerId }}
        </text>
    </svg>
</template>

<script>
import Player from "@/model/player.js";

export default {
    name: "v-player-piece",
    props: {
        player: {
            type: Player,
            required: true
        },
        xCenterPos: {
            type: Number,
            required: true
        },
        yCenterPos: {
            type: Number,
            required: true
        },
        interaction: {
            type: Boolean,
            required: false,
            default: false
        }
    },
    computed: {
        colorIndexClass: function() {
            return "player-piece__player-" + this.player.colorIndex;
        },
        isUser: function() {
            return this.player.isUser;
        },
        playerId: function() {
            return this.player.colorIndex;
        }
    }
};
</script>

<style lang="scss">
.player-piece {
    overflow: visible;

    &__shape {
        stroke: $color-player-stroke;
        stroke-width: 3px;
    }

    &__text {
        pointer-events: none;
        font-weight: bold;
        font-family: sans-serif;
        opacity: 0.8;

        &.player-piece--is-user {
            opacity: 1;
        }
    }

    &__halo {
        fill: none;
        stroke: $interaction-color;
        stroke-width: 2px;
        opacity: 1;
    }

    &__player-0 {
        .player-piece__shape {
            fill: $color-player-0;
        }

        .player-piece__text {
            fill: $text-color-player-0;
        }
    }

    &__player-1 {
        .player-piece__shape {
            fill: $color-player-1;
        }

        .player-piece__text {
            fill: $text-color-player-1;
        }
    }

    &__player-2 {
        .player-piece__shape {
            fill: $color-player-2;
        }

        .player-piece__text {
            fill: $text-color-player-2;
        }
    }

    &__player-3 {
        .player-piece__shape {
            fill: $color-player-3;
        }

        .player-piece__text {
            fill: $text-color-player-3;
        }
    }
}
</style>
