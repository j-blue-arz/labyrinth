<template>
    <footer class="footer__version">
        Version: {{ version }}&nbsp;&ndash;&nbsp;
        <a href="help.html" target="_blank" rel="noopener noreferrer">Help</a>&nbsp;&ndash;&nbsp;
        <a href="https://github.com/j-blue-arz/labyrinth" target="_blank" rel="noopener noreferrer">
            GitHub
        </a>
    </footer>
</template>

<script>
export default {
    name: "v-footer",
    data() {
        return {
            version: import.meta.env.VERSION,
        };
    },
};
</script>

<style lang="scss">
.footer__version {
    font-size: 0.8em;
    text-align: center;
}
</style>
