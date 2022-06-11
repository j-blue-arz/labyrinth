<template>
    <p @click="startEditing">
        <span v-show="!editing">{{ content }}</span>
        <span v-show="editing">
            <input
                v-model="editText"
                @blur="stopEditing"
                @keydown.enter="stopEditing"
                type="text"
                ref="input"
                class="editable__input"
            />
        </span>
    </p>
</template>

<script>
import Vue from "vue";

export default {
    name: "v-editable-field",
    data() {
        return {
            editing: false,
            editText: "",
        };
    },
    props: {
        placeholder: {
            type: String,
            default: "",
        },
        value: {
            type: String,
            required: true,
        },
    },
    emits: ["input"],
    computed: {
        content: function () {
            if (this.value === "") {
                return this.placeholder;
            } else {
                return this.value;
            }
        },
    },
    methods: {
        startEditing: function () {
            this.editing = true;
            Vue.nextTick(() => {
                this.$refs.input.focus();
            });
        },
        stopEditing: function () {
            this.editing = false;
            this.$emit("input", this.editText);
        },
    },
};
</script>

<style lang="scss">
.editable__input {
    width: 95%;
    padding: 0.2rem;
    border: 2px solid $color-input-border;
    border-radius: 4px;

    &:focus-visible {
        outline: none;
        border: 2px solid $interaction-color;
    }
}
</style>
