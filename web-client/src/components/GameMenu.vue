<template>
    <div @dblclick="onOpenMenu" class="game-menu__button">
        <v-menu
            @remove-computers="removeComputers"
            @replace-by-computer="replaceByComputer"
            @close-menu="closeMenu"
            :visible="menuIsVisible"
        />
    </div>
</template>


<script>
import VMenu from "@/components/VMenu.vue";

export default {
    name: "game-menu",
    props: {
        api: {
            required: true
        },
        game: {
            require: true
        },
        playerId: {
            type: Number,
            require: true
        }
    },
    components: {
        VMenu
    },
    data() {
        return {
            menuIsVisible: false
        };
    },
    methods: {
        onOpenMenu: function() {
            this.menuIsVisible = true;
        },
        removeComputers: function() {
            this.menuIsVisible = false;
            let computerPlayers = this.game.getComputerPlayers();
            let computerPlayerIds = computerPlayers.map(player => player.id);
            this.api
                .removePlayers(computerPlayerIds)
                .catch(this.handleError)
                .then(this.calledApiMethod);
        },
        replaceByComputer: function() {
            this.menuIsVisible = false;
            this.api
                .replacePlayer(this.playerId, "random")
                .catch(this.handleError)
                .then(this.calledApiMethod);
        },
        closeMenu: function() {
            this.menuIsVisible = false;
        },
        handleError: function(error) {
            console.error(error);
        },
        calledApiMethod: function() {
            this.$emit("called-api-method");
        }
    }
};
</script>

<style lang="scss">
.game-menu__button {
    display: block;
    height: 100px;
    width: 100px;
    position: absolute;
}
</style>
