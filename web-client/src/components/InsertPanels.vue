<template>
    <g>
        <v-insert-panel
            v-for="insertPanel in insertPanels"
            @panel-click="onClick($event, insertPanel)"
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
        n: {
            type: Number,
            required: false,
            default: 7
        }
    },
    computed: {
        insertPanels: function() {
            let result = [];
            let id = 0;
            let n = this.n;
            let border = n - 1;
            for (var position = 1; position < border; position += 2) {
                result.push(new InsertPanel(id++, -1, position, n));
                result.push(new InsertPanel(id++, position, -1, n));
                result.push(new InsertPanel(id++, n, position, n));
                result.push(new InsertPanel(id++, position, n, n));
            }
            for (var insertPanel of result) {
                if (this.locationsEqual(insertPanel.insertLocation, this.disabledInsertLocation)) {
                    insertPanel.enabled = false;
                } else {
                    insertPanel.enabled = true;
                }
            }
            return result;
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
        onClick: function(event, insertPanel) {
            if (this.interaction && insertPanel.enabled) {
                this.$emit("insert-panel-clicked", insertPanel.insertLocation);
            }
        }
    }
};
</script>
