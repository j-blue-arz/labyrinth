<template>
    <svg
        :height="cardSize"
        :width="cardSize"
        :id="mazeCard.id"
        :x="xPosAnimated"
        :y="yPosAnimated"
        :viewBox="`0 0 ${cardSize} ${cardSize}`"
        class="maze-card"
    >
        <g class="maze-card__group" :style="transformOriginStyle" :class="rotationClass">
            <rect
                x="0"
                y="0"
                :ry="edgeRadius"
                :height="cardSize"
                :width="cardSize"
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
                :x="(cardSize - 1) - (remainingSpace + 1)"
                :y="remainingSpace"
                :height="pathWidth"
                :width="remainingSpace + 1"
                class="maze-card__pathway"
            ></rect>
            <rect
                ref="southDoor"
                v-if="hasSouth"
                :x="remainingSpace"
                :y="(cardSize - 1) - (remainingSpace + 1)"
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
        <player-piece-group :players="players" :mid-point="piecesPosition" :max-size="piecesSize"/>
        <v-objective v-if="mazeCard.hasObject"></v-objective>
    </svg>
</template>

<script>
import MazeCard from "@/model/mazeCard.js";
import PlayerPieceGroup from "@/components/PlayerPieceGroup.vue";
import VObjective from "@/components/VObjective.vue";
import { TweenLite, Power3 } from "gsap";

const sizeToPiecesRatio = 3.5;
const sizeToPathWidthRatio = 2.7;
const sizeToEdgeRadiusRatio = 7;

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
        }
    },
    data() {
        return {
            animatedRotationClass: "",
            timer: 0,
            xPosAnimated: 0,
            yPosAnimated: 0
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
        players: function() {
            return this.mazeCard.players;
        },
        pathWidth: function() {
            return Math.floor(this.cardSize / sizeToPathWidthRatio);
        },
        edgeRadius: function() {
            return Math.floor(this.cardSize / sizeToEdgeRadiusRatio);
        },
        piecesSize: function() {
            return Math.floor(this.cardSize / sizeToPiecesRatio);
        },
        piecesPosition: function() {
            return Math.floor(this.cardSize / 2);
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
        },
        transformOriginStyle() {
            let mid = this.cardSize / 2;
            return "transform-origin: " + mid + "px " + mid + "px";
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

    &.interaction {
        .maze-card__outline {
            stroke-width: 2px;
            stroke-opacity: 1;
        }

        &:hover {
            .maze-card__outline {
                stroke: $color-outline-active;
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

    &.interaction {
        cursor: pointer;
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
</style>
