<template>
    <rect
        :height="size"
        :width="size"
        :x="xPos"
        :y="yPos"
        class="insert-location"
        :class="insertPanelClass"
    ></rect>
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
        insertPanelClass: function() {
            if (this.insertPanel.enabled) {
                if (this.interaction) {
                    return ["insert-location--enabled", "insert-location--interaction"];
                }
                return "insert-location--enabled";
            } else {
                return "insert-location--disabled";
            }
        }
    }
};
</script>

<style lang="scss">
.insert-location {
    transition: all 0.2s;
    &:not(&--interaction) {
        fill: black;
        opacity: 0.2;
    }

    &--interaction {
        opacity: 0.3;
        cursor: pointer;
        &:hover {
            fill: blue;
        }
    }
}
</style>
