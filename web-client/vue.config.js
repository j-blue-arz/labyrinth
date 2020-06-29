const path = require("path");

module.exports = {
    outputDir: path.resolve(__dirname, "../dist"),
    assetsDir: "static",
    configureWebpack: {
        devtool: "source-map"
    },
    lintOnSave: true,
    chainWebpack: config => {
        const types = ["vue-modules", "vue", "normal-modules", "normal"];
        types.forEach(type => addStyleResource(config.module.rule("scss").oneOf(type)));
    }
};

function addStyleResource(rule) {
    rule.use("style-resource")
        .loader("style-resources-loader")
        .options({
            patterns: [path.resolve(__dirname, "./src/scss/main.scss")]
        });
}
