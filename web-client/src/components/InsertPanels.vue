<template>
    <g>
        <v-insert-panel
            v-for="insertPanel in insertPanels"
            @click.native="onClick($event, insertPanel)"
            :key="'panel-' + insertPanel.id"
            :insert-panel="insertPanel"
            :x-pos="xPos(insertPanel)"
            :y-pos="yPos(insertPanel)"
            :size="cardSize"
            :interaction="interaction"
        />
    </g>
</template>

<script>
import VInsertPanel from "@/components/VInsertPanel.vue";
import InsertPanel from "@/model/insertPanel.js";

export default {
    name: "insert-panels",
    components: {
        VInsertPanel
    },
    props: {
        disabledInsertLocation: {
            type: Object,
            required: false,
            default: null
        },
        interaction: {
            type: Boolean,
            require: true
        },
        cardSize: {
            type: Number,
            required: false,
            default: 100
        },
        boardOffset: {
            type: Number,
            required: false,
            default: 100
        },
        mazeSize: {
            type: Number,
            required: false,
            default: 7
        }
    },
    data() {
        return {
            insertPanels: []
        };
    },
    watch: {
        disabledInsertLocation: function() {
            this.updateEnabledPanels();
        }
    },
    methods: {
        xPos(insertPanel) {
            return this.cardSize * insertPanel.displayLocation.column + this.boardOffset;
        },
        yPos(insertPanel) {
            return this.cardSize * insertPanel.displayLocation.row + this.boardOffset;
        },
        locationsEqual(locA, locB) {
            return locA && locB && locA.row === locB.row && locA.column === locB.column;
        },
        updateEnabledPanels: function() {
            for (var insertPanel of this.insertPanels) {
                if (this.locationsEqual(insertPanel.insertLocation, this.disabledInsertLocation)) {
                    insertPanel.enabled = false;
                } else {
                    insertPanel.enabled = true;
                }
            }
        },
        onClick: function(event, insertPanel) {
            if (this.interaction && insertPanel.enabled) {
                this.$emit("insert-panel-clicked", insertPanel.insertLocation);
            }
        }
    },
    created: function() {
        let id = 0;
        for (var position of [1, 3, 5]) {
            this.insertPanels.push(new InsertPanel(id++, -1, position));
            this.insertPanels.push(new InsertPanel(id++, position, -1));
            this.insertPanels.push(new InsertPanel(id++, this.mazeSize, position));
            this.insertPanels.push(new InsertPanel(id++, position, this.mazeSize));
        }
        this.updateEnabledPanels();
    }
};
</script>
