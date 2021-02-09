import Vue from "vue";
import App from "@/components/App.vue";

Vue.config.productionTip = false;

Vue.prototype.$ui = Object.freeze({
    cardSize: 100,
    boardOffset: 100
});

// https://stackoverflow.com/questions/36170425/detect-click-outside-element
Vue.directive("click-outside", {
    bind: function(el, binding, vnode) {
        el.clickOutsideEvent = function(event) {
            if (!(el == event.target || el.contains(event.target))) {
                vnode.context[binding.expression](event);
            }
        };
        document.body.addEventListener("click", el.clickOutsideEvent);
    },
    unbind: function(el) {
        document.body.removeEventListener("click", el.clickOutsideEvent);
    }
});

new Vue({
    render: function(h) {
        return h(App);
    }
}).$mount("#app");
