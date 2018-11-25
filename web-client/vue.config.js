const path = require("path");

module.exports = {
    outputDir: path.resolve(__dirname, "../dist"),
    assetsDir: "static",
    configureWebpack: {
        devtool: "source-map"
    },
    lintOnSave: true
};
