<template>
    <svg
        :height="cardSize"
        :width="cardSize"
        :id="mazeCard.id"
        :x="xPosAnimated"
        :y="yPosAnimated"
        viewBox="0 0 100 100"
        class="maze-card"
        :class="[{ 'maze-card--interactive': interaction }, reachablePlayerColorIndexClass]"
    >
        <g class="maze-card__group" :class="rotationClass">
            <rect
                ry="14"
                x="0"
                y="0"
                height="100"
                width="100"
                class="maze-card__wall maze-card__outline"
            ></rect>
            <rect
                :x="remainingSpace"
                :y="remainingSpace"
                :height="pathWidth"
                :width="pathWidth"
                class="maze-card__pathway"
            ></rect>
            <rect
                ref="northDoor"
                v-if="hasNorth"
                :x="remainingSpace"
                y="1"
                :height="remainingSpace"
                :width="pathWidth"
                class="maze-card__pathway"
            ></rect>
            <rect
                ref="eastDoor"
                v-if="hasEast"
                :x="98 - remainingSpace"
                :y="remainingSpace"
                :height="pathWidth"
                :width="remainingSpace + 1"
                class="maze-card__pathway"
            ></rect>
            <rect
                ref="southDoor"
                v-if="hasSouth"
                :x="remainingSpace"
                :y="98 - remainingSpace"
                :height="remainingSpace + 1"
                :width="pathWidth"
                class="maze-card__pathway"
            ></rect>
            <rect
                ref="westDoor"
                v-if="hasWest"
                x="1"
                :y="remainingSpace"
                :height="pathWidth"
                :width="remainingSpace"
                class="maze-card__pathway"
            ></rect>
        </g>
        <player-piece-group :players="players" :mid-point="50" :max-size="piecesSize" />
        <v-objective v-if="mazeCard.hasObject"></v-objective>
    </svg>
</template>

<script>
import MazeCard from "@/model/mazeCard.js";
import PlayerPieceGroup from "@/components/PlayerPieceGroup.vue";
import VObjective from "@/components/VObjective.vue";
import { TweenLite, Power3 } from "gsap";

export default {
    name: "v-maze-card",
    components: {
        /* eslint-disable vue/no-unused-components */
        PlayerPieceGroup,
        VObjective
    },
    props: {
        mazeCard: {
            type: MazeCard,
            required: true
        },
        cardSize: {
            type: Number,
            default: 100
        },
        xPos: {
            type: Number,
            required: false,
            default: 0
        },
        yPos: {
            type: Number,
            required: false,
            default: 0
        },
        interaction: {
            type: Boolean,
            required: false,
            default: false
        },
        reachableByPlayer: {
            required: false,
            default: null
        }
    },
    data() {
        return {
            animatedRotationClass: "",
            timer: 0,
            xPosAnimated: 0,
            yPosAnimated: 0,
            pathWidth: 37,
            piecesSize: 28
        };
    },
    watch: {
        rotation: function(newValue) {
            clearTimeout(this.timer);
            this.animatedRotationClass = "rotateTo" + newValue;
            this.timer = setTimeout(() => {
                this.animatedRotationClass = "rotate" + newValue;
            }, 500);
        },
        xPos: function(newValue) {
            TweenLite.to(this.$data, 1, { xPosAnimated: newValue, ease: Power3.easeInOut });
        },
        yPos: function(newValue) {
            TweenLite.to(this.$data, 1, { yPosAnimated: newValue, ease: Power3.easeInOut });
        }
    },
    computed: {
        rotation: function() {
            return this.mazeCard.rotation;
        },
        rotationClass: function() {
            if (this.animatedRotationClass === "") {
                return "rotate" + this.mazeCard.rotation;
            }
            return this.animatedRotationClass;
        },
        reachablePlayerColorIndexClass: function() {
            if (this.reachableByPlayer !== null) {
                return "maze-card--reachable-player-" + this.reachableByPlayer;
            }
            return "";
        },
        players: function() {
            return this.mazeCard.players;
        },
        remainingSpace: function() {
            return Math.floor((this.cardSize - this.pathWidth) / 2);
        },
        hasNorth: function() {
            return this.mazeCard.hasNorthDoor();
        },
        hasEast: function() {
            return this.mazeCard.hasEastDoor();
        },
        hasSouth: function() {
            return this.mazeCard.hasSouthDoor();
        },
        hasWest: function() {
            return this.mazeCard.hasWestDoor();
        }
    },
    created: function() {
        this.xPosAnimated = this.xPos;
        this.yPosAnimated = this.yPos;
    }
};
</script>

<style lang="scss">
.maze-card {
    &__outline {
        stroke: $color-outline;
        stroke-width: 1px;
        stroke-opacity: 0.8;
    }

    &--interactive {
        cursor: pointer;

        .maze-card__outline {
            stroke-width: 2px;
            stroke-opacity: 1;
            stroke: $interaction-color;
            animation: maze-card__outline--pulse 3s infinite;
        }

        &:hover {
            .maze-card__wall {
                fill: $interaction-color;
            }
        }
    }

    &__wall {
        fill: $color-walls;
    }

    &__pathway {
        fill: $color-pathways;
        stroke: $color-pathways;
    }

    &__group {
        transform-origin: 50px 50px;
    }

    &--reachable-player-0 {
        .maze-card__pathway {
            fill: $color-player-0-secondary;
            stroke: $color-player-0-secondary;
        }
    }

    &--reachable-player-1 {
        .maze-card__pathway {
            fill: $color-player-1-secondary;
            stroke: $color-player-1-secondary;
        }
    }

    &--reachable-player-2 {
        .maze-card__pathway {
            fill: $color-player-2-secondary;
            stroke: $color-player-2-secondary;
        }
    }

    &--reachable-player-3 {
        .maze-card__pathway {
            fill: $color-player-3-secondary;
            stroke: $color-player-3-secondary;
        }
    }
}

$degrees: 0 90 180 270;
@each $rotation in $degrees {
    $to: $rotation;
    @if $rotation == 0 {
        $to: 360;
    }
    $from: $to - 90;
    $animationName: from#{$from}to#{$to};

    .rotateTo#{$rotation} {
        @include rotationAnimation($animationName);
    }

    .rotate#{$rotation} {
        transform: rotate($rotation + deg);
    }

    @include rotateFromTo($animationName, $from + deg, $to + deg);
}

$color1: $color-outline;
$color2: $interaction-color;
@keyframes maze-card__outline--pulse {
    0% {
        stroke: $color1;
        stroke-width: 3px;
    }
    40% {
        stroke: $color1;
    }
    50% {
        stroke: $color2;
        stroke-width: 2px;
    }
    60% {
        stroke: $color1;
    }
    100% {
        stroke: $color1;
        stroke-width: 3px;
    }
}
</style>
