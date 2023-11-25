import VEditableField from "@/components/VEditableField.vue";
import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it } from "vitest";

beforeEach(() => {
    wrapper = factory();
});

describe("VEditableField", () => {
    it("has placeholder as content from the start", () => {
        thenContentIs(placeholder);
    });

    it("has placeholder as content if no text was set.", async () => {
        givenTextSet("");

        await whenFocusIsLost();

        thenContentIs(placeholder);
    });

    it("only shows one span when not editing.", () => {
        thenShowsOnlyOneSpan();
        thenInputIsInvisible();
    });

    it("only shows one span when editing.", async () => {
        await whenEnteringText();

        thenShowsOnlyOneSpan();
        thenInputIsVisible();
    });

    it("emits set text as event", async () => {
        givenTextSet("some text");

        await whenFocusIsLost();

        thenInputEventContentIs("some text");
    });
});

let wrapper = null;

let placeholder = "some placeholder";

const factory = function () {
    return mount(VEditableField, {
        props: {
            placeholder: placeholder,
            modelValue: "",
        },
    });
};

const givenTextSet = function (text) {
    wrapper
        .findAll("span")
        .filter((w) => w.isVisible())
        .at(0)
        .trigger("click");
    wrapper.find("input").setValue(text);
};

const whenFocusIsLost = async function () {
    await wrapper.find("input").trigger("blur");
};

const whenEnteringText = async function () {
    await wrapper
        .findAll("span")
        .filter((w) => w.isVisible())
        .at(0)
        .trigger("click");
};

const thenContentIs = function (expectedText) {
    let actualText = wrapper
        .findAll("span")
        .filter((w) => w.isVisible())
        .at(0)
        .text();
    expect(actualText).toEqual(expectedText);
};

const thenInputEventContentIs = function (expectedText) {
    expect(wrapper.emitted("update:modelValue")).toBeTruthy();
    expect(wrapper.emitted("update:modelValue")[0]).toEqual([expectedText]);
};

const thenShowsOnlyOneSpan = function () {
    let visibleSpans = wrapper.findAll("span").filter((w) => w.isVisible()).length;
    expect(visibleSpans).toEqual(1);
};

const thenInputIsInvisible = function () {
    expect(wrapper.find("input").isVisible()).toBeFalsy;
};

const thenInputIsVisible = function () {
    expect(wrapper.find("input").isVisible()).toBeTruthy;
};
