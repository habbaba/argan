/** @odoo-module **/

import Domain from 'web.Domain';
import {
    FLOAT_FIELDS,
    NUMERIC_FIELDS,
    INPUT_TYPE,
    checkFieldRangeMode,
    updateFieldRangeMode,
} from './main';
import { AdvancedSearchMixinForFieldsWithRange } from './advanvced_search_mixins';
import { patch } from 'web.utils';

const { Component } = owl;
const { useRef, useState, onMounted } = owl.hooks;

class AdvancedSearchNumericFieldInput extends Component {
    constructor(...args) {
        super(...args);

        this.inputRef = useRef('input');

        this.state= useState({
            showClearBtn: !!this.props.value,
        });
    }

    getValue() {
        return this.inputRef.el.value.trim();
    }

    updateClearBtn() {
        this.state.showClearBtn = !!this.inputRef.el.value;
    }

    onInputFocusin(event) {
        this.trigger('input-focusin');
    }

    onInputFocusout(event) {
        this.trigger('input-focusout');
    }

    onInputChange(event) {
        this.updateClearBtn();
    }

    onInput(event) {
        this.updateClearBtn();
    }

    onKeydownInput(event) {
        switch (event.key) {
            case 'Enter':
                this.trigger('input-enter-key');
                break;
        }
    }

    onClickClearBtn(event) {
        this.inputRef.el.value = '';
        this.state.showClearBtn = false;
        this.trigger('clear-input', {
            inputType: this.props.type,
        });
    }
}

AdvancedSearchNumericFieldInput.props = {
    value: String,
    type: {
        type: String,
        validate: prop => Object.values(INPUT_TYPE).includes(prop),
    },
};

AdvancedSearchNumericFieldInput.template = 'advanced_search_numeric_field_input';

class AdvancedSearchNumericField extends Component {
    constructor(...args) {
        super(...args);

        onMounted(this.onMounted.bind(this));

        this.INPUT_TYPE = INPUT_TYPE;

        this.state= useState({
            showOptionsPanel: false,
            rangeSearch: checkFieldRangeMode(this.props.viewId, this.props.field.name),
        });

        this.searchQuery = this.getSearchQuery(this.props.searchModelState, this.props.field.name, this.state.rangeSearch);
    }

    onMounted() {
        this.optionsPanelHeight = this.getOptionsPanelHeight();
    }

    getRangeSearchState() {
        return this.state.rangeSearch;
    }

    onClickSearchButton(event) {
        this.onSearch(this.getSearchValue('AdvancedSearchNumericFieldInput'));
    }

    onPressEnterKey(event) {
        this.onClickSearchButton();
    }

    onSearch(value) {
        let operator;
        if (!this.state.rangeSearch) {
            if (value === this.searchQuery) {
                return;
            }
            operator = '=';
        } else {
            if (value.from === this.searchQuery.from && value.to === this.searchQuery.to) {
                return;
            }
        }
        if (this.state.rangeSearch) {
            if (FLOAT_FIELDS.includes(this.props.field.type)) {
                if (value.from) {
                    value.from = parseFloat(value.from);
                }
                if (value.to) {
                    value.to = parseFloat(value.to);
                }
            } else {
                if (value.from) {
                    value.from = parseInt(value.from);
                }
                if (value.to) {
                    value.to = parseInt(value.to);
                }
            }
        } else if (value) {
            if (FLOAT_FIELDS.includes(this.props.field.type)) {
                value = parseFloat(value);
            } else {
                value = parseInt(value);
            }
        }
        this.env.bus.trigger('advanced-search', {
            fieldType: this.props.field.type,
            fieldName: this.props.field.name,
            operator,
            value,
            fieldString: this.props.field.string,
        });
    }
}

patch(AdvancedSearchNumericField.prototype, 'AdvancedSearchNumericField_Mixin', AdvancedSearchMixinForFieldsWithRange);

AdvancedSearchNumericField.components = {
    AdvancedSearchNumericFieldInput,
};

AdvancedSearchNumericField.props = {
    field: {
        type: Object,
        validate: prop => NUMERIC_FIELDS.includes(prop.type),
    },
    attrs: Object,
    searchModelState: Object,
    viewId: Number,
};

AdvancedSearchNumericField.template = 'advanced_search_numeric_field';

export {
    AdvancedSearchNumericField,
}
