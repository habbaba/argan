/** @odoo-module **/

import {
    RELATION_FIELDS,
} from './main';
import { AdvancedSearchSelectionField } from './advanced_search_selection_field';
import { DropPrevious } from 'web.concurrency';
import { py_eval } from 'web.py_utils';

const { useRef, useState } = owl.hooks;

const DEBOUNCE_LOAD_AUTOCOMPLETE_LIST_TIMEOUT = 500;

class AdvancedSearchRelationField extends AdvancedSearchSelectionField {
    constructor(...args) {
        super(...args);

        this.dropPrevAutocomplete = new DropPrevious();
        this.debounceLoadAutocompleteList = _.debounce(
            this.debounceLoadAutocompleteList.bind(this), DEBOUNCE_LOAD_AUTOCOMPLETE_LIST_TIMEOUT);

        this.updateAutocompleteListState();

		if (this.props.attrs.options) {
			let options = py_eval(this.props.attrs.options);
			this.selectionDomain = options.selection_domain;
		}
    }

    getQueryLabel(query) {
        let label;
        let filter = this.props.searchModelState.filters[query.filterId];
        if (filter) {
            label = filter.valueDisplayName;
        }
        return label;
    }

    getAutocompleteList(value) {
        return [];
    }

    updateAutocompleteListState(list) {
        if (!list) {
            this.state.autocompleteList = [[false, 'Not set']];
            return;
        }
        this.state.autocompleteList = list
            .filter(e => !this.searchQueries.map(e => e.value).includes(e[0]));
    }

    debounceLoadAutocompleteList() {
        let value = this.inputRef.el.value.trim();
        if (!value) {
            this.state.showLoadingSpinner = false;
            this.updateAutocompleteListState();
            return;
        }
        this.dropPrevAutocomplete.add(this.loadAutocompleteList(value)).then((res) => {
            this.state.showLoadingSpinner = false;
            if (!this.inputRef.el.value.trim()) {
                this.updateAutocompleteListState();
                return;
            }
            this.state.showAutocomplete = true;
            this.updateAutocompleteListState(res);
        });
    }

    async loadAutocompleteList(value) {
        return await this.env.services.rpc({
            model: this.props.field.relation,
            method: 'name_search',
            kwargs: {
                name: value,
                args: this.selectionDomain || [],
            }
        });
    }

    onInput(event) {
        this.state.showLoadingSpinner = true;
        this.debounceLoadAutocompleteList();
    }

    onFocusinInput(event) {
        if (this.state.autocompleteList.length) {
            this.state.showAutocomplete = true;
        }
        this.updateInputPlaceholder();
    }

    onSearch(value) {
        let item = this.state.autocompleteList.find(e => e[0] === value);
        let displayName = item ? item[1] : value;
        this.state.showAutocomplete = false;
        this.env.bus.trigger('advanced-search', {
            fieldType: this.props.field.type,
            fieldName: this.props.field.name,
            operator: this.domainOperator,
            value,
            fieldString: this.props.field.string,
            relation: true,
            valueDisplayName: displayName,
        });
    }
}

AdvancedSearchRelationField.props = {
    ...AdvancedSearchSelectionField.props,
    field: {
        type: Object,
        validate: prop => RELATION_FIELDS.includes(prop.type),
    },
};

export {
    AdvancedSearchRelationField,
}
