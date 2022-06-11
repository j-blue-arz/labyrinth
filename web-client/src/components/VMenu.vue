<template>
    <ul class="menu" v-click-outside="reset">
        <li
            v-for="item in visibleMenuItems"
            :key="item.key"
            :ref="item.key"
            class="menu__item"
            @click.stop="onItemClick(item)"
        >
            {{ item.text }}
        </li>
    </ul>
</template>

<script>
export default {
    name: "v-menu",
    props: {
        menuItems: {
            required: true,
        },
    },
    data() {
        return {
            activeMenuKey: null,
        };
    },
    computed: {
        visibleMenuItems: function () {
            if (this.activeMenuKey === null) {
                return this.menuItems;
            } else {
                let activeMenu = this.findMenuitem(this.activeMenuKey, this.menuItems);
                if (activeMenu) {
                    let result = [];
                    result.push(activeMenu);
                    for (var subItem of activeMenu.submenu) {
                        result.push(subItem);
                    }
                    return result;
                } else {
                    return this.menuItems;
                }
            }
        },
    },
    methods: {
        findMenuitem(searchKey, menuItems) {
            for (let menuItem of menuItems) {
                if (menuItem.key === searchKey) {
                    return menuItem;
                }
                if (menuItem.hasSubmenu()) {
                    let recurseResult = this.findMenuitem(searchKey, menuItem.submenu);
                    if (recurseResult) {
                        return recurseResult;
                    }
                }
            }
            return null;
        },
        onItemClick(item) {
            if (item.hasSubmenu()) {
                this.activeMenuKey = item.key;
            } else {
                this.$emit("item-click", item.key);
                this.reset();
            }
        },
        reset() {
            this.activeMenuKey = null;
        },
    },
};
</script>

<style lang="scss">
.menu {
    list-style: none;
    margin: 0;

    &__item {
        display: flex;
        cursor: pointer;
        padding: 0.5rem 1rem;
        align-items: center;
        border-bottom: 1px solid grey;
        background: $color-menu-background;

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
