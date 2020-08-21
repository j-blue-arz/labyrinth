<template>
    <ul class="menu" v-show="visible">
        <li
            v-for="item in visibleMenuItems"
            :key="item.key"
            :ref="item.key"
            class="menu__item"
            @click="onItemClick(item)"
        >
            {{ item.text }}
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
    watch: {
        visible: function(newValue, oldValue) {
            if (!oldValue && newValue) {
                this.visibleMenuItems.splice(0, this.visibleMenuItems.length);
                for (var item of this.menuItems) {
                    this.visibleMenuItems.push(item);
                }
            }
        }
    },
    data() {
        return {
            visibleMenuItems: []
        };
    },
    methods: {
        onItemClick(item) {
            if (item.hasSubmenu()) {
                this.visibleMenuItems.splice(0, this.visibleMenuItems.length);
                this.visibleMenuItems.push(item);
                for (var subItem of item.submenu) {
                    this.visibleMenuItems.push(subItem);
                }
            } else {
                this.$emit("item-click", item.key);
            }
        }
    }
};
</script>

<style lang="scss">
.menu {
    list-style: none;
    position: absolute;
    left: -3rem;
    top: 2rem;

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
