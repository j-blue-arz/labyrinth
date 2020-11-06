<template>
    <svg height="100" width="100" viewBox="0 0 100 100" class="leftover">
        <v-maze-card
            @click.native="onLeftoverClick"
            v-if="hasStarted"
            :maze-card="mazeCard"
            x="0"
            y="0"
            :interaction="interaction"
            class="leftover__card"
            ref="leftover"
        ></v-maze-card>
        <path v-if="interaction" :d="arrowPath" class="leftover__arrow"></path>
        <polygon v-if="interaction" :points="arrowHead" class="leftover__arrow-head"></polygon>
    </svg>
</template>

<script>
import VMazeCard from "@/components/VMazeCard.vue";
import MazeCard from "@/model/mazeCard.js";

export default {
    name: "leftover-maze-card",
    components: {
        /* eslint-disable vue/no-unused-components */
        VMazeCard
    },
    props: {
        mazeCard: {
            type: MazeCard,
            required: true
        },
        landscape: {
            type: Boolean,
            required: false,
            default: true
        },
        isLandscape: {
            type: Boolean,
            required: false,
            default: true
        },
        interaction: {
            type: Boolean,
            required: false,
            default: false
        }
    },
    computed: {
        hasStarted: function() {
            return this.mazeCard instanceof MazeCard;
        },
        leftoverSize: function() {
            return this.$ui.cardSize * 1.6;
        },
        width: function() {
            if (this.isLandscape) {
                return this.$ui.cardSize * 1.5;
            } else {
                return this.$ui.cardSize;
            }
        },
        height: function() {
            if (this.isLandscape) {
                return this.$ui.cardSize;
            } else {
                return this.$ui.cardSize * 1.5;
            }
        },
        mazeCardX: function() {
            if (this.isLandscape) {
                return this.$ui.cardSize;
            } else {
                return 0;
            }
        },
        mazeCardY: function() {
            if (this.isLandscape) {
                return 0;
            } else {
                return this.$ui.cardSize;
            }
        },
        arrowPath: function() {
            let radius = 40;
            let start = 0.7 * radius;
            let pathStart = [50 - start, 50 + start];
            let arc = [radius, radius, 0, 1, 1, 50 + start, 50 + start];
            return "M" + pathStart + "A" + arc;
        },
        arrowHead: function() {
            let radius = 40;
            let start = 0.7 * radius;
            let arrowLength = 20;
            let point1 = [50 + start - 4, 50 + start + 4];
            let point2 = [point1[0], point1[1] - arrowLength];
            let point3 = [point1[0] + arrowLength, point1[1]];
            return [point1, point2, point3];
        }
    },
    methods: {
        onLeftoverClick: function() {
            if (this.interaction) {
                this.mazeCard.rotateClockwise();
            }
        }
    }
};
</script>

<style lang="scss">
@mixin arrow {
    opacity: 1;
    animation: leftover__interaction-arrow--pulse 3s infinite;
    cursor: pointer;
    pointer-events: none;
}

.leftover {
    overflow: visible;

    &__card {
        overflow: visible;
    }

    &__arrow {
        @include arrow;
        fill: none;
        stroke: $interaction-color;
    }

    &__arrow-head {
        @include arrow;
        fill: $interaction-color;
        stroke: none;
    }

    &:hover {
        .leftover__arrow {
            opacity: 0;
        }

        .leftover__arrow-head {
            opacity: 0;
        }
    }
}
$width: 12;
@include pulsating-stroke-width(leftover__interaction-arrow--pulse, $width + 1, $width - 1);
</style>
