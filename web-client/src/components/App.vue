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
        let useStorage = process.env.NODE_ENV === "production";
        this.controller = new Controller(useStorage);
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
    font-family: Helvetica, sans-serif;
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

.app {
    height: 100%;
    width: 100%;

    &__main {
        height: 100%;
        width: 100%;
        display: grid;

        @media (orientation: landscape) {
            grid-template-columns: 1fr auto 1fr;
            grid-template-areas: ". game .";
        }

        @media (orientation: portrait) {
            grid-template-areas: "game";
        }
    }

    &__game {
        grid-area: game;
        height: 100%;
        width: 100%;
    }
}

html {
    font-size: 12px;

    @media (min-width: 1200px) {
        font-size: 16px;
    }

    @media (min-width: 320px) {
        font-size: calc(12px + 4 * (100vw - 320px) / 880);
    }
}

/*@media all and (orientation: landscape) {
    .game__board {
        height: 100%;
    }
}

@media all and (orientation: portrait) {
    .game__board {
        width: 100%;
    }
}*/
</style>
