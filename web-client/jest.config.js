module.exports = {
    preset: "@vue/cli-plugin-unit-jest",
    testMatch: ["**/tests/**/*.spec.(js|jsx|ts|tsx)"],
    setupFiles: ["<rootDir>/tests/jest.init.js"],
};
