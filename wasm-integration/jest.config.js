module.exports = {
    moduleFileExtensions: ["js"],
    testPathIgnorePatterns: [
      "/node_modules/"
    ],
    transform: {
        "^.+\\.jsx?$": "babel-jest"
    },
    moduleNameMapper: {
        "^@/(.*)$": "<rootDir>/$1"
    },
    testMatch: ["**/test/*.test.js"],
    collectCoverage: false
};
