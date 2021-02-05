<template>
    <ul class="menu" @click="reset">
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
            required: true
        }
    },
    data() {
        return {
            visibleMenuItems: []
        };
    },
    methods: {
        onItemClick(item) {
            console.log("onclick");
            if (item.hasSubmenu()) {
                console.log("hassub" + item.submenu.length);
                this.visibleMenuItems.splice(0, this.visibleMenuItems.length);
                this.visibleMenuItems.push(item);
                for (var subItem of item.submenu) {
                    this.visibleMenuItems.push(subItem);
                }
            } else {
                this.$emit("item-click", item.key);
            }
        },
        reset() {
            console.log("reset");
            this.visibleMenuItems.splice(0, this.visibleMenuItems.length);
            for (var item of this.menuItems) {
                this.visibleMenuItems.push(item);
            }
        }
    },
    created: function() {
        this.reset();
    }
};
</script>

<style lang="scss">
.menu {
    width: 100%;
    height: 100%;

    list-style: none;
    padding: 1rem 0;
    margin: 0;

    &__item {
        display: flex;
        cursor: pointer;
        padding: 8px 15px;
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
