<template>
    <svg
        ref="playerPiece"
        class="player-piece"
        :class="[{'player-piece__user': isUser, 'player-piece__user--to-move': isUser && hasToMove},
        colorIndexClass]"
    >
        <circle
            :cx="xCenterPos"
            :cy="yCenterPos"
            :r="maxSize/2"
            class="player-piece__shape"
        />
        <circle
            v-if="hasToMove && isUser"
            :cx="xCenterPos"
            :cy="yCenterPos"
            :r="maxSize/2 + 2"
            fill="none"
            stroke="blue"
            class="player-piece__halo"
        ></circle>
        <text
            :x="xCenterPos"
            :y="yCenterPos"
            :textLength="maxSize/2"
            :font-size="maxSize-3"
            class="player-piece__text"
            dominant-baseline="central"
            text-anchor="middle"
        >{{ playerId }}</text>
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
        }
    },
    computed: {
        colorIndexClass: function() {
            return "player-piece__player-" + this.player.colorIndex;
        },
        isUser: function() {
            return this.player.isUser;
        },
        hasToMove: function() {
            return this.player.hasToMove();
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
        opacity: $opacity-player-not-user;
    }

    &__text {
        pointer-events: none;
        font-weight: bold;
        font-family: sans-serif;
        opacity: $opacity-player-not-user;
    }

    &__halo {
        fill: none;
        stroke: $color-outline-active;
        stroke-width: 2px;
        opacity: 1;
    }

    &__user {
        .player-piece__shape {
            opacity: 1;
        }

        .player-piece__text {
            opacity: 1;
        }

        &--to-move {
            .player-piece__halo {
                animation: player-piece__halo--pulse 1s infinite;
            }
        }
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

@include pulsating("player-piece__halo--pulse");
</style>
