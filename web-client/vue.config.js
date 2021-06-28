const webpack = require("webpack");

const path = require("path");
const compressionPlugin = require("compression-webpack-plugin");

const version = require("./package.json").version;

module.exports = {
    assetsDir: "assets",
    configureWebpack: {
        devtool: "source-map",
        plugins: [
            new webpack.DefinePlugin({
                "process.env": {
                    VERSION: '"' + version + '"'
                }
            })
        ]
    },
    lintOnSave: true,
    css: {
        loaderOptions: {
            sass: {
                additionalData: `@import "@/scss/main.scss";`
            }
        }
    },
    chainWebpack: config => {
        config.plugin("CompressionPlugin").use(compressionPlugin);
    }
};
