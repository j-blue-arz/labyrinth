<template>
    <svg
        :viewBox="`0 0 ${size} ${size}`"
        :height="size"
        :width="size"
        class="insert-panel"
        :class="insertPanelClass"
        :x="xPos"
        :y="yPos">
        <rect
            :height="size"
            :width="size"
            class="insert-panel__click-area"
            @click="onClick"
        />
        <transition name="insert-panel__fade-animation-">
            <path
                v-if="isDisabled"
                :d="pathCross"
                class="insert-panel__symbol insert-panel__cross"
            />
        </transition>
        <transition name="insert-panel__fade-animation-">
            <path
                v-if="isEnabled"
                :id="'panel-path-' + insertPanel.id"
                @click="onClick"
                :d="pathArrow"
                class="insert-panel__symbol insert-panel__arrow"
            />
        </transition>
    </svg>

</template>

<script>
import InsertPanel from "@/model/insertPanel.js";

export default {
    name: "v-insert-panel",
    props: {
        insertPanel: {
            type: InsertPanel,
            required: true
        },
        size: {
            type: Number,
            required: true
        },
        xPos: {
            type: Number,
            required: true
        },
        yPos: {
            type: Number,
            required: true
        },
        interaction: {
            type: Boolean,
            required: false,
            default: true
        }
    },
    computed: {
        isEnabled: function() {
            return this.insertPanel.enabled;
        },
        isDisabled: function() {
            return !this.insertPanel.enabled;
        },
        insertPanelClass: function() {
            if (this.insertPanel.enabled) {
                if (this.interaction) {
                    return ["insert-panel--enabled", "insert-panel--interaction"];
                }
                return "insert-panel--enabled";
            } else {
                if (this.interaction) {
                    return ["insert-panel--disabled", "insert-panel--interaction"];
                }
                return "insert-panel--disabled";
            }
        },
        pathCross: function() {
            let paths = [[[25, 25], [75, 75]], [[75, 25], [25, 75]]];
            return "M" + paths.join("M");
        },
        pathArrow: function() {
            let paths = [[[25, 45], [50, 25], [75, 45]], [[25, 70], [50, 50], [75, 70]]];
            this.rotateAndTranslatePaths(paths);
            return "M" + paths.join("M");
        },
        transformOriginStyle() {
            let mid = this.size / 2;
            return "transform-origin: " + mid + "px " + mid + "px";
        }
    },
    methods: {
        rotateAndTranslatePaths(paths) {
            let mid = this.size / 2;
            let angle = this.angle();
            if (angle !== 0) {
                for (var path of paths) {
                    for (var point of path) {
                        point[0] = point[0] - mid;
                        point[1] = point[1] - mid;
                        let q = [0, 0];
                        q[0] = point[0] * Math.cos(angle) - point[1] * Math.sin(angle);
                        q[1] = point[0] * Math.sin(angle) + point[1] * Math.cos(angle);
                        point[0] = Math.round(q[0] + mid);
                        point[1] = Math.round(q[1] + mid);
                    }
                }
            }
        },
        angle: function() {
            if (this.isDisabled) {
                return 0;
            }
            let degree = ["N", "E", "S", "W"].indexOf(this.insertPanel.direction) * 90;
            return 2 * Math.PI * (degree / 360.0);
        },
        onClick: function() {
            this.$emit("panel-click");
        }
    }
};
</script>

<style lang="scss">
.insert-panel {
    stroke-linejoin: round;
    stroke-linecap: round;
    stroke-width: 12;

    &path {
        transition: all 1s;
    }

    &:not(&--interaction) {
        .insert-panel__cross {
            stroke: $disabled-color-secondary;
        }

        .insert-panel__arrow {
            stroke: $interaction-color-secondary;
        }
    }

    &--interaction {
        filter: none;

        .insert-panel__arrow {
            cursor: pointer;
            filter: url(#drop-shadow);
        }

        .insert-panel__click-area {
            cursor: pointer;
        }
    }

    &__symbol {
        fill: none;
        transition: stroke 0.3s;
    }

    &__cross {
        stroke: $disabled-color;
    }

    &__arrow {
        stroke: $interaction-color;
    }

    &__click-area {
        fill: white;
        opacity: 0.1;
    }

    &__fade-animation {
        &--enter-active,
        &--leave-active {
            transition: opacity 1s;
        }

        &--enter,
        &--leave-to {
            opacity: 0;
        }
    }
}
</style>
