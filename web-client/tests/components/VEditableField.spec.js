import { mount } from "@vue/test-utils";
import VEditableField from "@/components/VEditableField.vue";

beforeEach(() => {
    wrapper = factory();
});

describe("VEditableField", () => {
    it("has placeholder as content from the start", () => {
        thenContentIs(placeholder);
    });

    it("has placeholder as content if no text was set.", () => {
        givenTextSet("");

        whenFocusIsLost();

        thenContentIs(placeholder);
    });

    it("only shows one span when not editing.", () => {
        thenShowsOnlyOneSpan();
        thenInputIsInvisible();
    });

    it("only shows one span when editing.", () => {
        whenEnteringText();

        thenShowsOnlyOneSpan();
        thenInputIsVisible();
    });

    it("emits set text as event", () => {
        givenTextSet("some text");

        whenFocusIsLost();

        thenInputEventContentIs("some text");
    });
});

let wrapper = null;

let placeholder = "some placeholder";

const factory = function () {
    let wrapper = mount(VEditableField, {
        propsData: {
            placeholder: placeholder,
            value: "",
        },
    });
    return wrapper;
};

const givenTextSet = function (text) {
    wrapper
        .findAll("span")
        .filter((w) => w.isVisible())
        .at(0)
        .trigger("click");
    wrapper.find("input").setValue(text);
};

const whenFocusIsLost = function () {
    wrapper.find("input").trigger("blur");
};

const whenEnteringText = function () {
    wrapper
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
    expect(wrapper.emitted().input).toBeTruthy();
    expect(wrapper.emitted().input[0]).toEqual([expectedText]);
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
