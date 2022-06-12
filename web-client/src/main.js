import { createApp } from "vue";
import App from "@/components/App.vue";
import store from "@/store";

// https://stackoverflow.com/questions/36170425/detect-click-outside-element
const clickOutside = {
    beforeMount: (el, binding) => {
        el.clickOutsideEvent = (event) => {
            if (!(el == event.target || el.contains(event.target))) {
                binding.value();
            }
        };
        document.addEventListener("click", el.clickOutsideEvent);
    },
    unmounted: (el) => {
        document.removeEventListener("click", el.clickOutsideEvent);
    },
};

const app = createApp(App);
app.config.globalProperties.$ui = Object.freeze({
    cardSize: 100,
});

app.use(store).directive("click-outside", clickOutside).mount("#app");
