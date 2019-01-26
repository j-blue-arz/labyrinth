<template>
    <ul class="menu" v-show="visible">
        <li
            v-for="item in menuItems"
            :key="item.key"
            :ref="item.key"
            class="menu__item"
            @click="onItemClick(item)">
            {{item.name}}
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
        },
        menuItems: {
            required: true
        }
    },
    methods: {
        onItemClick(item) {
            this.$emit("item-click", item.key);
        }
    }
};
</script>

<style lang="scss">
.menu {
    list-style: none;
    position: absolute;
    left: -11rem;
    top: 0.5rem;

    &__item {
        display: flex;
        cursor: pointer;
        padding: 8px 15px;
        align-items: center;
        border-bottom: 1px solid grey;
        font-family: sans-serif;
        background: $color-menu-background;
        white-space: nowrap;

        &:hover {
            background: $color-menu-hover;
            color: $color-menu-background;
        }

        &:last-child {
            border: none;
        }
    }
}
</style>
