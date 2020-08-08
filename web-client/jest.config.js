module.exports = {
    moduleFileExtensions: ["js", "jsx", "json", "vue"],
    transform: {
        "^.+\\.vue$": "<rootDir>/node_modules/vue-jest",
        ".+\\.(css|styl|less|sass|scss|svg|png|jpg|ttf|woff|woff2)$": "<rootDir>/node_modules/jest-transform-stub",
        "^.+\\.jsx?$": "<rootDir>/node_modules/babel-jest"
    },
    moduleNameMapper: {
        "^@/(.*)$": "<rootDir>/src/$1"
    },
    snapshotSerializers: ["jest-serializer-vue"],
    testMatch: ["**/tests/unit/**/*Test.(js|jsx|ts|tsx)"],
    testURL: "http://localhost/",
    collectCoverage: false,
    collectCoverageFrom: ["**/src/**.{js,vue}", "!**/node_modules/**"]
};
