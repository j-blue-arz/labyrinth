<template>
    <svg
        ref="playerPiece"
        class="player-piece"
        :class="[
            { 'player-piece__user': isUser, 'player-piece__user--to-move': isUser && interaction },
            colorIndexClass
        ]"
        :viewBox="`0 0 ${svgSize} ${svgSize}`"
        :height="`${svgSize}px`"
        :width="`${svgSize}px`"
    >
        <circle :cx="xCenterPos" :cy="yCenterPos" :r="maxSize / 2" class="player-piece__shape" />
        <circle
            v-if="interaction && isUser"
            :cx="xCenterPos"
            :cy="yCenterPos"
            :r="maxSize / 2 + 2"
            class="player-piece__halo"
        ></circle>
        <text
            :x="xCenterPos"
            :y="yCenterPos"
            :textLength="maxSize / 2"
            :font-size="maxSize - 3"
            class="player-piece__text"
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
        maxSize: {
            type: Number,
            required: true
        },
        svgSize: {
            type: Number,
            required: false,
            default: 100
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
    &__shape {
        stroke: $color-player-stroke;
        stroke-width: 3px;
    }

    &__text {
        pointer-events: none;
        font-weight: bold;
        font-family: sans-serif;
        opacity: $text-opacity-player-not-user;

        .player-piece__user {
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

            .player-piece__user {
                fill: $color-player-0-secondary;
            }
        }
        .player-piece__text {
            fill: $text-color-player-0;
        }
    }

    &__player-1 {
        .player-piece__shape {
            fill: $color-player-1;

            .player-piece__user {
                fill: $color-player-1-secondary;
            }
        }
        .player-piece__text {
            fill: $text-color-player-1;
        }
    }

    &__player-2 {
        .player-piece__shape {
            fill: $color-player-2;

            .player-piece__user {
                fill: $color-player-2-secondary;
            }
        }
        .player-piece__text {
            fill: $text-color-player-2;
        }
    }

    &__player-3 {
        .player-piece__shape {
            fill: $color-player-3;

            .player-piece__user {
                fill: $color-player-3-secondary;
            }
        }
        .player-piece__text {
            fill: $text-color-player-3;
        }
    }
}
</style>
