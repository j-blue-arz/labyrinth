const path = require("path");
const compressionPlugin = require("compression-webpack-plugin");

module.exports = {
    outputDir: path.resolve(__dirname, "../backend/static"),
    assetsDir: "assets",
    configureWebpack: {
        devtool: "source-map"
    },
    lintOnSave: true,
    css: {
        loaderOptions: {
            sass: {
                additionalData: `@import "@/scss/main.scss";`
            }
        }
    },
    chainWebpack: config => {config.plugin("CompressionPlugin").use(compressionPlugin);}
};
