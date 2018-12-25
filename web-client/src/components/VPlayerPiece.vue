<template>
<svg
    class="player-piece">
    <circle
        ref="playerPiece"
        :cx="xCenterPos"
        :cy="yCenterPos"
        :r="maxSize/2"
        class="player-piece__circle"
        :class="[{'player-piece__user': isUser}, fillColorClass]"/>
    <circle
        :cx="xCenterPos"
        :cy="yCenterPos"
        :r="maxSize/2 + 2"
        fill="none"
        stroke="blue"
        class="player-piece__halo player-piece__user--to-move"
        v-if="hasToMove && isUser"/>
    <text
        :x="xCenterPos"
        :y="yCenterPos"
        :textLength="maxSize/2"
        :font-size="maxSize-3"
        :class="textColorClass"
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
            require: true
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
    computed: {
        textColorClass: function() {
            return "player-piece__player-" + this.player.colorIndex + "--text";
        },
        fillColorClass: function() {
            return "player-piece__player-" + this.player.colorIndex + "--fill";
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
    &__circle {
        stroke: $color-player-stroke;
        stroke-width: 3px;
        opacity: $opacity-player-not-user;
    }

    &__text {
        pointer-events: none;
        font-weight: bold;
        font-family: sans-serif;
    }

    &__halo {
        fill: none;
        stroke: $color-outline-active;
        stroke-width: 2px;
        opacity: 1;
    }

    &__user {
        opacity: 1;

        &--to-move {
            animation: halo-pulse 1s infinite;
        }
    }

    &__player-0 {
        &--fill {
            fill: $color-player-0;
        }
        &--text {
            fill: $text-color-player-0;
        }
    }

    &__player-1 {
        &--fill {
            fill: $color-player-1;
        }
        &--text {
            fill: $text-color-player-1;
        }
    }

    &__player-2 {
        &--fill {
            fill: $color-player-2;
        }
        &--text {
            fill: $text-color-player-2;
        }
    }

    &__player-3 {
        &--fill {
            fill: $color-player-3;
        }
        &--text {
            fill: $text-color-player-3;
        }
    }
}

@include pulsating("halo-pulse");
</style>
