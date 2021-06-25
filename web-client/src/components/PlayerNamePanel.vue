<template>
    <v-editable-field
        v-if="isEditable"
        v-model="player.playerName"
        @input="onChangeName"
        :placeholder="editablePlaceholder"
    />
    <p v-else>{{ playerLabel }}</p>
</template>

<script>
import VEditableField from "@/components/VEditableField.vue";
import Player from "@/model/player.js";

export default {
    name: "player-name-panel",
    components: {
        VEditableField
    },
    data() {
        return {
            editablePlaceholder: "You (edit here)"
        };
    },
    props: {
        player: {
            type: Player,
            required: true
        },
        controller: {
            type: Object,
            required: true
        }
    },
    computed: {
        isEditable: function() {
            return this.player.isUser;
        },
        playerLabel: function() {
            return this.player.getLabel();
        }
    },
    methods: {
        onChangeName: function() {
            this.controller.changeUserPlayerName(this.player.playerName);
        }
    }
};
</script>

<style></style>
