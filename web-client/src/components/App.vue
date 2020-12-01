<template>
    <game-container />
</template>

<script>
import GameContainer from "@/components/GameContainer.vue";

export default {
    name: "app",
    components: {
        GameContainer
    },
    data() {
        return {};
    }
};
</script>

<style lang="scss">
* {
    font-family: Cambria, serif;
}

body {
    height: 100vh;
    width: 100vw;
    margin: 0;
}
</style>
