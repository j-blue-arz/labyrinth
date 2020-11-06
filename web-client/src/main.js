import Vue from "vue";
import App from "@/components/App.vue";

Vue.config.productionTip = false;

Vue.prototype.$ui = Object.freeze({
    cardSize: 100,
    boardOffset: 100
});

new Vue({
    render: function(h) {
        return h(App);
    }
}).$mount("#app");
