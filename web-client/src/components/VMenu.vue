<template>
    <ul class="menu" v-show="visible">
        <li
            class="menu__item"
            ref="close"
            @click="onCloseClick">
            close
        </li>
        <li
            class="menu__item"
            ref="remove"
             @click="onRemoveComputersClick">
             remove
        </li>
        <li
            class="menu__item"
            ref="exhaustive"
            @click="onReplaceByExhaustiveClick">
            replace by exhaustive search
        </li>
        <li
            class="menu__item"
            ref="minimax"
            @click="onReplaceByMinimaxClick">
            replace by minimax
        </li>
    </ul>
</template>

<script>
export default {
    name: "v-menu",
    props: {
        visible: {
            type: Boolean,
            required: true
        }
    },
    methods: {
        onCloseClick() {
            this.$emit("close-menu");
        },
        onRemoveComputersClick() {
            this.$emit("remove-computers");
        },
        onReplaceByExhaustiveClick() {
            this.$emit("replace-by-exhaustive");
        },
        onReplaceByMinimaxClick() {
            this.$emit("replace-by-minimax");
        }
    }
};
</script>

<style lang="scss">
.menu {
    list-style: none;
    position: absolute;

    &__item {
        display: flex;
        cursor: pointer;
        padding: 8px 15px;
        align-items: center;
        border-bottom: 1px solid grey;
        font-family: sans-serif;

        &:hover {
            background: orange;
            color: white;
        }

        &:last-child {
            border: none;
        }
    }
}
</style>
