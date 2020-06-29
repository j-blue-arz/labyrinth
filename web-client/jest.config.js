module.exports = {
    moduleFileExtensions: ["js", "jsx", "json", "vue"],
    transform: {
        "^.+\\.vue$": "vue-jest",
        ".+\\.(css|styl|less|sass|scss|svg|png|jpg|ttf|woff|woff2)$": "jest-transform-stub",
        "^.+\\.jsx?$": "babel-jest"
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
