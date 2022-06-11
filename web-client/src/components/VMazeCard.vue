<template>
    <svg
        :height="$ui.cardSize"
        :width="$ui.cardSize"
        :id="mazeCard.id"
        :x="xPosAnimated"
        :y="yPosAnimated"
        viewBox="0 0 100 100"
        class="maze-card"
        :class="[
            { 'maze-card--interactive': interaction, 'maze-card--shiftable': shiftInteraction },
            reachablePlayerColorIndexClass,
        ]"
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
                ref="north"
                v-if="hasNorth"
                :x="remainingSpace"
                y="1"
                :height="remainingSpace"
                :width="pathWidth"
                class="maze-card__pathway"
            ></rect>
            <rect
                ref="east"
                v-if="hasEast"
                :x="98 - remainingSpace"
                :y="remainingSpace"
                :height="pathWidth"
                :width="remainingSpace + 1"
                class="maze-card__pathway"
            ></rect>
            <rect
                ref="south"
                v-if="hasSouth"
                :x="remainingSpace"
                :y="98 - remainingSpace"
                :height="remainingSpace + 1"
                :width="pathWidth"
                class="maze-card__pathway"
            ></rect>
            <rect
                ref="west"
                v-if="hasWest"
                x="1"
                :y="remainingSpace"
                :height="pathWidth"
                :width="remainingSpace"
                class="maze-card__pathway"
            ></rect>
        </g>
        <player-piece-group :players="players" :mid-point="50" :max-size="piecesSize" />
        <v-objective v-if="hasObjective"></v-objective>
    </svg>
</template>

<script>
import PlayerPieceGroup from "@/components/PlayerPieceGroup.vue";
import VObjective from "@/components/VObjective.vue";
import { TweenLite, Power3 } from "gsap";

export default {
    name: "v-maze-card",
    components: {
        /* eslint-disable vue/no-unused-components */
        PlayerPieceGroup,
        VObjective,
    },
    props: {
        mazeCard: {
            type: Object,
            required: true,
        },
        xPos: {
            type: Number,
            required: false,
            default: 0,
        },
        yPos: {
            type: Number,
            required: false,
            default: 0,
        },
        interaction: {
            type: Boolean,
            required: false,
            default: false,
        },
        shiftInteraction: {
            type: Boolean,
            required: false,
            default: false,
        },
        reachableByPlayer: {
            required: false,
            default: null,
        },
    },
    data() {
        return {
            animatedRotationClass: "",
            timer: 0,
            xPosAnimated: 0,
            yPosAnimated: 0,
            pathWidth: 37,
            piecesSize: 33,
            positionAnimationThreshold: 40,
        };
    },
    watch: {
        rotation: function (newValue) {
            clearTimeout(this.timer);
            this.animatedRotationClass = "rotateTo" + newValue;
            this.timer = setTimeout(() => {
                this.animatedRotationClass = "rotate" + newValue;
            }, 500);
        },
        xPos: function (newValue, oldValue) {
            if (Math.abs(newValue - oldValue) > this.positionAnimationThreshold) {
                TweenLite.to(this.$data, 0.9, { xPosAnimated: newValue, ease: Power3.easeInOut });
            } else {
                this.xPosAnimated = newValue;
            }
        },
        yPos: function (newValue, oldValue) {
            if (Math.abs(newValue - oldValue) > this.positionAnimationThreshold) {
                TweenLite.to(this.$data, 0.9, { yPosAnimated: newValue, ease: Power3.easeInOut });
            } else {
                this.yPosAnimated = newValue;
            }
        },
    },
    computed: {
        rotation: function () {
            return this.mazeCard.rotation;
        },
        rotationClass: function () {
            if (this.animatedRotationClass === "") {
                return "rotate" + this.mazeCard.rotation;
            }
            return this.animatedRotationClass;
        },
        reachablePlayerColorIndexClass: function () {
            if (this.reachableByPlayer !== null) {
                return "maze-card--reachable-player-" + this.reachableByPlayer;
            }
            return "";
        },
        players: function () {
            return this.$store.getters["players/findByMazeCard"](this.mazeCard.id);
        },
        remainingSpace: function () {
            return Math.floor((this.$ui.cardSize - this.pathWidth) / 2);
        },
        hasNorth: function () {
            return this.hasOutPath(this.mazeCard, "N");
        },
        hasEast: function () {
            return this.hasOutPath(this.mazeCard, "E");
        },
        hasSouth: function () {
            return this.hasOutPath(this.mazeCard, "S");
        },
        hasWest: function () {
            return this.hasOutPath(this.mazeCard, "W");
        },
        hasObjective: function () {
            return this.$store.state.game.objectiveId === this.mazeCard.id;
        },
    },
    methods: {
        hasOutPath(mazeCard, outPath) {
            return mazeCard.outPaths.indexOf(outPath) != -1;
        },
    },
    created: function () {
        this.xPosAnimated = this.xPos;
        this.yPosAnimated = this.yPos;
    },
};
</script>

<style lang="scss">
.maze-card {
    &__outline {
        stroke: $color-outline-noninteractive;
        stroke-width: 1px;
        stroke-opacity: 0.8;
    }

    &__wall {
        fill: $color-walls;
        opacity: 0.9;
    }

    &--interactive {
        cursor: pointer;

        .maze-card__outline {
            stroke: $color-outline-interactive;
            stroke-width: 3px;
            stroke-opacity: 1;
            stroke: $interaction-color;
            animation: maze-card__outline--pulse 3s infinite;
        }

        .maze-card__wall {
            opacity: 1;
        }

        &:hover {
            .maze-card__wall {
                fill: $interaction-color;
            }
        }
    }

    &--shiftable {
        cursor: grab;

        &:active:hover {
            cursor: grabbing;
        }

        .maze-card__outline {
            stroke: $color-outline-interactive;
            stroke-width: 3px;
            stroke-opacity: 0.8;
        }

        .maze-card__wall {
            opacity: 1;
        }
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

$color1: $color-outline-interactive;
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
