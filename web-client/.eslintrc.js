module.exports = {
    root: true,
    env: {
        node: true
    },
    extends: ["plugin:vue/essential", "@vue/prettier"],
    rules: {
        //"no-console": process.env.NODE_ENV === "production" ? "error" : "off",
        "no-console": "off",
        "no-debugger": process.env.NODE_ENV === "production" ? "error" : "off",
        "max-len": [
            1,
            {
                code: 100,
                tabWidth: 2
            }
        ]
    },
    parserOptions: {
        parser: "babel-eslint"
    }
};
