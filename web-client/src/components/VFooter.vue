<template>
    <div class="footer__version">Version: {{ version }}</div>
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
