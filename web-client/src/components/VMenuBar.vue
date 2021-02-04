<template>
    <game-menu :controller="controller" />
</template>

<script>
import GameMenu from "@/components/GameMenu.vue";

export default {
    name: "v-menu-bar",
    props: {
        controller: {
            type: Object,
            required: true
        }
    },
    components: {
        GameMenu
    },
    data() {
        return {};
    }
};
</script>

<style>
</style>
