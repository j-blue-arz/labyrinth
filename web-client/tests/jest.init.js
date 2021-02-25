import { config } from "@vue/test-utils";

config.mocks["$ui"] = Object.freeze({
    cardSize: 100
});
