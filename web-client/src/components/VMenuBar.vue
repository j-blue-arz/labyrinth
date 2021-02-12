<template>
    <div class="menubar">
        <input
            id="menubar-toggle"
            class="menubar__checkbox"
            type="checkbox"
            autocomplete="off"
            v-model="menuToggled"
        />
        <label for="menubar-toggle" class="menubar__toggle">
            <span class="menubar__toggle-symbol" />
        </label>
        <div class="menubar__slider">
            <game-menu
                :controller="controller"
                @item-click="resetToggle"
                v-click-outside="resetToggle"
            />
            <v-footer />
        </div>
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
    data() {
        return {
            menuToggled: false
        };
    },
    components: {
        GameMenu,
        VFooter
    },
    methods: {
        resetToggle() {
            if (this.menuToggled) {
                this.menuToggled = false;
            }
        }
    }
};
</script>

<style lang="scss">
.menubar {
    z-index: 1;

    &__slider {
        z-index: 3;

        background: $color-background;
        width: $menubar-width;
        height: 100%;

        @include drop-shadow;
        border: 1px solid $color-ui-border;
        padding: 1rem 0;

        display: flex;
        flex-flow: column nowrap;
        justify-content: space-between;

        position: fixed;
        transform: translateX(calc(-100% - 10px));
        transition: transform 200ms;
    }

    &__checkbox {
        display: none;
    }

    &__checkbox:checked ~ &__slider {
        transform: translateX(0);
    }

    &__toggle {
        z-index: 2;

        background-color: $color-menu-background;
        height: var(--menubar-toggle-size);
        width: var(--menubar-toggle-size);
        position: fixed;
        top: 1rem;
        left: 1rem;
        @include drop-shadow;
        text-align: center;
        cursor: pointer;
    }

    &__toggle-symbol {
        position: relative;
        margin-top: calc(var(--menubar-toggle-size) * 0.5);

        &,
        &::before,
        &::after {
            width: calc(var(--menubar-toggle-size) * 0.75);
            height: 2px;
            background-color: $text-color;
            display: inline-block;
        }

        &::before,
        &::after {
            content: "";
            position: absolute;
            left: 0;
            transition: top 0.1s;
        }

        &::before {
            top: calc(var(--menubar-toggle-size) * -0.25);
        }
        &::after {
            top: calc(var(--menubar-toggle-size) * 0.25);
        }
    }

    &__toggle:hover {
        background-color: $color-menu-hover;
    }

    &__toggle:hover &__toggle-symbol::before {
        top: calc(var(--menubar-toggle-size) * -0.3);
    }

    &__toggle:hover &__toggle-symbol::after {
        top: calc(var(--menubar-toggle-size) * 0.3);
    }
}
</style>
