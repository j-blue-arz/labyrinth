<template>
    <v-editable-field v-if="isEditable" v-model="playerName" :placeholder="editablePlaceholder" />
    <p v-else>{{ playerLabel }}</p>
</template>

<script>
import VEditableField from "@/components/VEditableField.vue";
import { getLabel } from "@/model/player.js";

import { mapActions } from "pinia";
import { usePlayersStore } from "@/stores/players.js";

export default {
    name: "player-name-panel",
    components: {
        VEditableField,
    },
    data() {
        return {
            editablePlaceholder: "You (edit here)",
        };
    },
    props: {
        player: {
            required: true,
        },
    },
    computed: {
        isEditable: function () {
            return this.player.isUser;
        },
        playerLabel: function () {
            return getLabel(this.player);
        },
        playerName: {
            get() {
                return this.player.name;
            },
            set(value) {
                this.changeUserPlayerName(value);
            },
        },
    },
    methods: {
        ...mapActions(usePlayersStore, ["changeUserPlayerName"]),
    },
};
</script>

<style></style>
