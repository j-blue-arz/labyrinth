<template>
    <div class="menubar">
        <game-menu :controller="controller" />
    </div>
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

<style lang="scss">
.menubar {
    @include drop-shadow;
    height: 100%;
    border: 1px solid $color-ui-border;
}
</style>
