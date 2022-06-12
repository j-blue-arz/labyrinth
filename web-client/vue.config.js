const webpack = require("webpack");
const { defineConfig } = require("@vue/cli-service");

const compressionPlugin = require("compression-webpack-plugin");

const version = require("./package.json").version;

module.exports = defineConfig({
    assetsDir: "assets",
    configureWebpack: {
        devtool: "source-map",
        plugins: [
            new webpack.DefinePlugin({
                "process.env.VERSION": '"' + version + '"',
            }),
        ],
    },
    lintOnSave: true,
    css: {
        loaderOptions: {
            sass: {
                additionalData: `@import "@/scss/main.scss";`,
            },
        },
    },
    productionSourceMap: false,
    chainWebpack: (config) => {
        config.plugin("CompressionPlugin").use(compressionPlugin);
    },
});
