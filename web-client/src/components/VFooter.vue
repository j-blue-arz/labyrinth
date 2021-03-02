<template>
    <footer class="footer__version">
        Version: {{ version }}&nbsp;&ndash;&nbsp;
        <a href="help.html" target="_blank" rel="noopener noreferrer">Help</a>
    </footer>
</template>

<script>
export default {
    name: "v-footer",
    data() {
        return {
            version: process.env.VERSION
        };
    }
};
</script>

<style lang="scss">
.footer__version {
    font-size: 0.8em;
    text-align: center;
}
</style>
