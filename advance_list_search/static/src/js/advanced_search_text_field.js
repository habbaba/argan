/** @odoo-module **/

import Domain from 'web.Domain';
import {
    FLOAT_FIELDS,
    NUMERIC_FIELDS,
    TEXT_FIELDS,
    SIMPLE_FIELDS,
} from './main';

const { Component } = owl;
const { useRef, useState } = owl.hooks;

class AdvancedSearchTextField extends Component {
    constructor(...args) {
        super(...args);

        this.inputRef = useRef('input');

        this.searchQuery = '';
        let filter = Object.values(this.props.searchModelState.filters)
            .find(f => f.type === 'filter' && !!f.advancedSearch && f.fieldName === this.props.field.name);
        if (filter) {
            let searchQuery = this.props.searchModelState.query
                .find(e => e.filterId === filter.id);
            if (searchQuery && filter.domain) {
                let domainArray = Domain.prototype.stringToArray(filter.domain);
                this.searchQuery = domainArray[0][2];
            }
        }

        this.state= useState({
            showClearBtn: !!this.searchQuery,
        });
    }

    onClickSearchButton(event) {
        this.onSearch();
    }

    onInput(event) {
        this.state.showClearBtn = !!this.inputRef.el.value;
    }

    onKeydownInput(event) {
        switch (event.key) {
            case 'Enter':
                this.onSearch();
                break;
        }
    }

    onClickClearBtn(event) {
        this.inputRef.el.value = '';
        this.state.showClearBtn = false;
        this.onSearch();
    }

    onSearch() {
        let value = this.inputRef.el.value.trim();
        if (value === this.searchQuery) {
            return;
        }
        this.env.bus.trigger('advanced-search', {
            fieldType: this.props.field.type,
            fieldName: this.props.field.name,
            operator: 'ilike',
            value,
            fieldString: this.props.field.string,
        });
    }
}

AdvancedSearchTextField.props = {
    field: {
        type: Object,
        validate: prop => TEXT_FIELDS.includes(prop.type),
    },
    attrs: Object,
    searchModelState: Object,
    viewId: Number,
};

AdvancedSearchTextField.template = 'advanced_text_simple_field';

export {
    AdvancedSearchTextField,
}
