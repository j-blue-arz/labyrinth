<template>
    <div @dblclick="onOpenMenu" class="game-menu game-menu__button">
        <v-menu
            @remove-computers="removeComputers"
            @replace-by-exhaustive="replaceByExhaustive"
            @replace-by-minimax="replaceByMinimax"
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
        userPlayerId: {
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
        replaceByExhaustive: function() {
            this.replaceByComputer("exhaustive-single");
        },
        replaceByMinimax: function() {
            this.replaceByComputer("minimax");
        },
        replaceByComputer: function(type) {
            this.menuIsVisible = false;
            this.api
                .replacePlayer(this.userPlayerId, type)
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
    background-color: lightblue;
}
</style>
