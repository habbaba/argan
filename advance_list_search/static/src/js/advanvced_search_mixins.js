/** @odoo-module **/

import Domain from 'web.Domain';
import { INPUT_TYPE, updateFieldRangeMode } from './main';

export const AdvancedSearchMixinForFieldsWithRange = {
    getSearchQuery(searchModelState, fieldName, rangeSearch) {
        let value = !rangeSearch ? false : { from: false, to: false };
        let filter = Object.values(searchModelState.filters)
            .find(f => f.type === 'filter' && !!f.advancedSearch && f.fieldName === fieldName);
        if (filter) {
            let searchQuery = searchModelState.query
                .find(e => e.filterId === filter.id);
            if (searchQuery && filter.domain) {
                let domainArray = Domain.prototype.stringToArray(filter.domain);
                if (!rangeSearch) {
                    value = domainArray[0][2].toString();
                } else {
                    if (domainArray.length > 1) {
                        value.from = domainArray.find(e => e[1].includes('>'))[2].toString();
                        value.to = domainArray.find(e => e[1].includes('<'))[2].toString();
                    } else if (domainArray.length === 1) {
                        let queryValue = domainArray[0][2];
                        if (domainArray[0][1].includes('>')) {
                            value.from = queryValue.toString();
                        } else if (domainArray[0][1].includes('<')) {
                            value.to = queryValue.toString();
                        }
                    }
                }
            }
        }
        return value;
    },

    getOptionsPanelHeight() {
        let th = this.el.closest('thead').querySelector('th');
        return th.clientHeight + 1;
    },

    onFocusinOptionsPanel(event) {
        this.state.showOptionsPanel = true;
    },

    onClickToggleRangeBtn(event) {
        if (this.getRangeSearchState()) {
            if (!!this.searchQuery.from || !!this.searchQuery.to) {
                this.onSearch({
                    from: false,
                    to: false,
                });
            }
        } else {
            if (!!this.searchQuery) {
                this.onSearch(false);
            }
        }
        this.state.rangeSearch = !this.state.rangeSearch;
        this.searchQuery = this.getRangeSearchState() ? { from: false, to: false } : false;
        updateFieldRangeMode(this.props.viewId, this.props.field.name, this.state.rangeSearch);
    },

    onMouseenterWidget(event) {
        this.state.showOptionsPanel = true;
    },

    onMouseleaveWidget(event) {
        if (!this.inputIsFocus) {
            this.state.showOptionsPanel = false;
        }
    },

    onInputFocusin(event) {
        this.state.showOptionsPanel = true;
        this.inputIsFocus = true;
    },

    onInputFocusout(event) {
        this.state.showOptionsPanel = false;
        this.inputIsFocus = false;
    },

    onClearInput(event) {
        if (!this.state.rangeSearch) {
            this.onSearch(false);
        } else {
            if (event.detail.inputType === INPUT_TYPE.FROM) {
                this.onSearch({
                    from: false,
                    to: this.searchQuery.to,
                });
            } else if (event.detail.inputType === INPUT_TYPE.TO) {
                this.onSearch({
                    from: this.searchQuery.from,
                    to: false,
                });
            }
        }
    },

    onClickClearRangeBtn(event) {
        if (this.state.rangeSearch) {
            this.onSearch({
                from: false,
                to: false,
            });
        }
    },

    getSearchValue(componentName) {
        let inputComponents = Object.values(this.__owl__.children)
            .filter(e => e.constructor.name === componentName);
        if (this.state.rangeSearch) {
            let fromValue = false;
            let toValue = false;
            let fromInput = inputComponents.find(e => e.props.type === INPUT_TYPE.FROM);
            if (fromInput) {
                fromValue = fromInput.getValue();
            }
            let toInput = inputComponents.find(e => e.props.type === INPUT_TYPE.TO);
            if (toInput) {
                toValue = toInput.getValue();
            }
            return {
                from: fromValue,
                to: toValue,
            };
        } else {
            let input = inputComponents.find(e => e.props.type === INPUT_TYPE.SINGLE);
            if (!input) {
                return;
            }
            return input.getValue();
        }
    }
};
