<template>
    <div class="menubar">
        <game-menu :controller="controller" />
        <v-footer />
    </div>
</template>

<script>
import GameMenu from "@/components/GameMenu.vue";
import VFooter from "@/components/VFooter.vue";

export default {
    name: "v-menu-bar",
    props: {
        controller: {
            type: Object,
            required: true
        }
    },
    components: {
        GameMenu,
        VFooter
    }
};
</script>

<style lang="scss">
.menubar {
    @include drop-shadow;
    border: 1px solid $color-ui-border;
    padding: 1rem 0;
    display: flex;
    flex-flow: column nowrap;
    justify-content: space-between;
}
</style>
