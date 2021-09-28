<template>
    <div class="app">
        <v-menu-bar class="app__menubar" :controller="controller" />
        <div class="app__main">
            <v-game class="app__game" :controller="controller" />
        </div>
    </div>
</template>

<script>
import VMenuBar from "@/components/VMenuBar.vue";
import Controller from "@/controllers/controller.js";
import VGame from "@/components/VGame.vue";

export default {
    name: "app",
    components: {
        VMenuBar,
        VGame
    },
    data() {
        return {
            controller: null
        };
    },
    created: function() {
        this.controller = new Controller();
        window.addEventListener("beforeunload", () => this.controller.beforeDestroy());
        this.controller.initialize();
    },
    beforeDestroy() {
        this.controller.beforeDestroy();
    }
};
</script>

<style lang="scss">
* {
    font-family: "Play", Helvetica, sans-serif;
}

*,
::after,
::before {
    box-sizing: inherit;
    padding: 0;
    margin: 0;
}

html {
    box-sizing: border-box;
}

body {
    height: 100vh;
    width: 100vw;
    margin: 0;
    color: $text-color;
    background: $color-background;
    overflow: hidden;
}

input {
    font-family: inherit;
    font-size: inherit;
}

.app {
    height: 100%;

    &__main {
        height: 100%;
        display: grid;

        @media (orientation: landscape) {
            grid-template-columns: 1vmin 1fr auto 1fr 1vmin;
            grid-template-areas: ". . game . .";
        }

        @media (orientation: portrait) {
            grid-template-columns: 1vmin 1fr 1vmin;
            grid-template-rows: 1vmin 1fr 1vmin;
            grid-template-areas: ". . . " ". game ." ". . .";
        }
    }

    &__game {
        grid-area: game;
        height: 100%;
    }
}

html {
    font-size: 11px;

    @media (min-width: 320px) {
        font-size: calc(11px + (100vw - 320px) / 40);
    }

    @media (min-width: 360px) {
        font-size: calc(12px + 4 * (100vw - 360px) / 840);
    }

    @media (min-width: 1200px) {
        font-size: 16px;
    }
}
</style>
