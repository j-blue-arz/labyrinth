require('@rushstack/eslint-patch/modern-module-resolution')

module.exports = {
    root: true,
    env: {
        node: true,
        es2022: true,
    },
    extends: ["plugin:vue/vue3-essential", "eslint:recommended", "@vue/eslint-config-prettier/skip-formatting"],
    rules: {
        //"no-console": process.env.NODE_ENV === "production" ? "error" : "off",
        "no-console": "off",
        "no-debugger": process.env.NODE_ENV === "production" ? "error" : "off",
        "max-len": [
            1,
            {
                code: 120,
                tabWidth: 2,
            },
        ],
    },
};
