import { config } from "@vue/test-utils";

config.global.mocks["$ui"] = Object.freeze({
    cardSize: 100,
});
