/** @odoo-module **/

import Domain from 'web.Domain';
import {
    SELECTION_FIELD,
} from './main';

const { Component } = owl;
const { useRef, useState, onPatched } = owl.hooks;

class AdvancedSearchSelectionField extends Component {
    constructor(...args) {
        super(...args);

        onPatched(this.onPatched.bind(this));

        this.inputRef = useRef('input');
        this.autocompleteRef = useRef('autocomplete');

        this.searchQueries = [];
        this.filters = Object.values(this.props.searchModelState.filters)
            .filter(f => f.type === 'filter' && !!f.advancedSearch && f.fieldName === this.props.field.name && !!f.domain);
        if (this.filters.length) {
            let searchQueriesFilterIds = this.props.searchModelState.query.map(e => e.filterId);
            this.filters = this.filters.filter(e => searchQueriesFilterIds.includes(e.id));
            this.searchQueries = this.filters.map(f => {
                return {
                    value: Domain.prototype.stringToArray(f.domain)[0][2],
                    filterId: f.id,
                    groupId: f.groupId,
                }
            });
        }

        this.state= useState({
            autocompleteList: this.getAutocompleteList(),
            disableClearAllBtn: !!this.searchQuery,
            showAutocomplete: false,
            showLoadingSpinner: false,
        });

        this.domainOperator = '=';
    }

    onPatched() {
        if (this.autocompleteRef.el) {
            let autocompleteEl = this.autocompleteRef.el;
            let scrollWidth = autocompleteEl.scrollWidth;
            let offsetWidth = autocompleteEl.offsetWidth;
            let autocompleteIsEmpty = autocompleteEl.querySelector('.advanced_search_selection_autocomplete_list_empty');
            if (scrollWidth > offsetWidth && !autocompleteIsEmpty) {
                let scrollHeight = autocompleteEl.scrollHeight;
                let offsetHeight = autocompleteEl.offsetHeight;
                let scrollBarWidth = 10;
                let width = scrollWidth + 8;
                if (scrollHeight > offsetHeight) {
                    width += scrollBarWidth;
                }
                autocompleteEl.style.width = width + 'px';
                let rect = autocompleteEl.getBoundingClientRect();
                if (rect.x + width > window.innerWidth) {
                    autocompleteEl.style.right = 0;
                    autocompleteEl.style.left = 'unset';
                }
            } else {
                autocompleteEl.style.width = '100%';
            }
        }
    }

    getQueryLabel(query) {
        let label;
        let select = this.props.field.selection.find(e => e[0] === query.value);
        if (select) {
            label = select[1];
        } else if (query.value === false) {
            label = 'Not set';
        }
        return label;
    }

    getAutocompleteList(value) {
        let list = this.props.field.selection
            .filter(e => (value ? e[1].toLowerCase().includes(value.toLowerCase()) : true) && !this.searchQueries.map(e => e.value).includes(e[0]));
        if (!this.props.field.required && list.length) {
            list = [[false, 'Not set'], ...list]
        }
        return list;
    }

    updateAutocompleteListState() {
        let inputVal = this.inputRef.el.value.trim();
        this.state.autocompleteList = this.getAutocompleteList(inputVal);
    }

    updateInputPlaceholder() {
        if ([this.inputRef.el, this.autocompleteRef.el].includes(document.activeElement)) {
            this.inputRef.el.placeholder = 'Enter 1 or more characters';
        } else {
            this.inputRef.el.placeholder = '';
        }
    }

    getAutocompleteFocusedItem() {
        let items = this.el.querySelectorAll('.advanced_search_selection_autocomplete_list_item');
        return Array.from(items).find(e => e === document.activeElement);
    }

    getAutocompleteItemByIndex(index) {
        return this.el.querySelector(`.advanced_search_selection_autocomplete_list_item[data-item-index="${index}"]`);
    }

    onClickInputBlock(event) {
        event.stopPropagation();
        if (this.inputRef.el !== document.activeElement) {
            this.inputRef.el.focus();
        }
    }

    onKeydownInput(event) {
        event.stopPropagation();
        switch (event.key) {
            case 'ArrowUp':
                event.stopPropagation();
                break;
            case 'ArrowDown':
                let item = this.el.querySelector('div[data-item-index="0"]');
                if (item) {
                    item.focus();
                }
                break;
        }
    }

    onInput(event) {
        this.updateAutocompleteListState();
    }

    onFocusinInput(event) {
        this.state.showAutocomplete = true;
        this.updateInputPlaceholder();
    }

    onFocusoutInput(event) {
        setTimeout(() => {
            if (this.getAutocompleteFocusedItem()) {
                return;
            }
            this.updateInputPlaceholder();
            this.state.showAutocomplete = false;
        }, 50);
    }

    onKeydownAutocompleteItem(value, event) {
        event.stopPropagation();
        event.preventDefault();
        let item = event.target;
        let itemIndex = parseInt(item.dataset.itemIndex);
        switch (event.key) {
            case 'ArrowUp':
                if (itemIndex === 0) {
                    this.inputRef.el.focus();
                } else if (itemIndex > 0) {
                    let prevItem = this.autocompleteRef.el.querySelector(`[data-item-index="${itemIndex - 1}"]`);
                    prevItem.focus();
                }
                break;
            case 'ArrowDown':
                if (item !== this.autocompleteRef.el.lastChild) {
                    let nextItem = this.autocompleteRef.el.querySelector(`[data-item-index="${itemIndex + 1}"]`);
                    nextItem.focus();
                }
                break;
            case 'Enter':
                this.onSearch(value);
                break;
        }
    }

    onFocusoutAutocomplete(event) {
        setTimeout(() => {
            if ([this.autocompleteRef.el, this.inputRef.el,...Array.from(this.autocompleteRef.el.children)]
                .includes(document.activeElement)) {
                return;
            }
            this.updateInputPlaceholder();
            this.state.showAutocomplete = false;
        }, 50);
    }

    onMouseenterAutocompleteItem(event) {
        let focusedItem = this.getAutocompleteFocusedItem();
        if (focusedItem) {
            this.inputRef.el.focus();
        }
    }

    onClickAutocompleteItem(value, event) {
        this.onSearch(value);
    }

    onClickRemoveQuery(filterId, event) {
        event.stopPropagation();
        this.env.bus.trigger('advanced-search-remove-filter', filterId);
    }

    onClickRemoveAll(event) {
        let groupIds = [...new Set(this.searchQueries.map(e => e.groupId))];
        if (groupIds.length) {
            this.env.bus.trigger('advanced-search-remove-filter-group', groupIds);
        } else {
            this.inputRef.el.value = '';
            this.updateAutocompleteListState();
        }
    }

    onSearch(value) {
        this.state.showAutocomplete = false;
        let displayName = value;
        let item = this.state.autocompleteList.find(e => e[0] === value);
        if (item) {
            displayName = item[1];
        }
        this.env.bus.trigger('advanced-search', {
            fieldType: this.props.field.type,
            fieldName: this.props.field.name,
            operator: this.domainOperator,
            value,
            fieldString: this.props.field.string,
            valueDisplayName: displayName,
        });
    }
}
AdvancedSearchSelectionField.props = {
    field: {
        type: Object,
        validate: prop => SELECTION_FIELD === prop.type,
    },
    attrs: Object,
    searchModelState: Object,
    viewId: Number,
};

AdvancedSearchSelectionField.template = 'advanced_search_selection_field';

export {
    AdvancedSearchSelectionField,
}
