import { config } from "@vue/test-utils";
import Vue from "vue";

Vue.directive("click-outside", {});

config.mocks["$ui"] = Object.freeze({
    cardSize: 100
});
