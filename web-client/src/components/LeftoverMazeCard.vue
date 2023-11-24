<template>
    <svg viewBox="0 0 100 100" class="leftover">
        <v-maze-card
            @click="onLeftoverClick"
            :maze-card="mazeCard"
            x="0"
            y="0"
            :interaction="shiftInteraction"
            class="leftover__card"
            ref="leftover"
        ></v-maze-card>
        <path v-if="shiftInteraction" :d="arrowPath" class="leftover__arrow"></path>
        <polygon v-if="shiftInteraction" :points="arrowHead" class="leftover__arrow-head"></polygon>
    </svg>
</template>

<script>
import VMazeCard from "@/components/VMazeCard.vue";
import * as action from "@/model/player.js";

import { mapState, mapActions } from "pinia";
import { useBoardStore } from "@/stores/board.js";
import { usePlayersStore } from "@/stores/players.js";

export default {
    name: "leftover-maze-card",
    components: {
        /* eslint-disable vue/no-unused-components */
        VMazeCard,
    },
    computed: {
        rotation: function () {
            return this.mazeCard.rotation;
        },
        arrowPath: function () {
            let radius = 40;
            let start = 0.7 * radius;
            let pathStart = [50 - start, 50 + start];
            let arc = [radius, radius, 0, 1, 1, 50 + start, 50 + start];
            return "M" + pathStart + "A" + arc;
        },
        arrowHead: function () {
            let radius = 40;
            let start = 0.7 * radius;
            let arrowLength = 20;
            let point1 = [50 + start - 4, 50 + start + 4];
            let point2 = [point1[0], point1[1] - arrowLength];
            let point3 = [point1[0] + arrowLength, point1[1]];
            return [point1, point2, point3];
        },
        ...mapState(useBoardStore, {
            mazeCard: (store) => store.leftoverMazeCard,
        }),
        ...mapState(usePlayersStore, {
            shiftInteraction: (store) => store.userPlayer?.nextAction === action.SHIFT_ACTION,
        }),
    },
    methods: {
        onLeftoverClick: function () {
            if (this.shiftInteraction) {
                this.rotateLeftoverClockwise();
            }
        },
        ...mapActions(useBoardStore, ["rotateLeftoverClockwise"]),
    },
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
