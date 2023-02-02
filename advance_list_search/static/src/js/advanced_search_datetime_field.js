/** @odoo-module **/

import Domain from 'web.Domain';
import {
    DATE_FIELD,
    DATETIME_FIELD,
    INPUT_TYPE,
    checkFieldRangeMode,
    updateFieldRangeMode,
    checkFieldDatetimeAsDateMode,
    updateFieldDatetimeAsDateMode,
} from './main';
import { DateWidget, DateTimeWidget } from 'web.datepicker';
import { patch } from 'web.utils';
import { AdvancedSearchMixinForFieldsWithRange } from './advanvced_search_mixins';

const { Component } = owl;
const { useRef, useState, onMounted, onPatched } = owl.hooks;

const DATE_FORMAT = 'YYYY-MM-DD';
const DATETIME_FORMAT = 'YYYY-MM-DD HH:mm:ss';

DateWidget.include({
    _onInput: function (ev) {
        this._super(...arguments);
        this.trigger('datetime_input');
    },
});

class AdvancedSearchDatetimeFieldInput extends Component {
    constructor(...args) {
        super(...args);

        onMounted(this.onMounted.bind(this));
        onPatched(this.onPatched.bind(this));

        this.datepickerWrapperRef = useRef('datepicker_wrapper');

        this.state= useState({
            showClearBtn: !!this.searchQuery,
        });

        this.currentDateAsDatetime = this.props.datetimeAsDate;
    }

    onMounted() {
        if (!this.datepicker) {
            this.initDatepicker();
        }
    }

    onPatched() {
        if (this.currentDateAsDatetime !== this.props.datetimeAsDate) {
            this.currentDateAsDatetime = this.props.datetimeAsDate;
            this.initDatepicker();
        }
    }

    initDatepicker() {
        let options = {};
        if (this.datepicker) {
            this.datepicker.destroy();
        }
        if (this.props.isDatetime && !this.props.datetimeAsDate) {
            this.datepicker = new DateTimeWidget(this, options);
        } else {
            this.datepicker = new DateWidget(this, options);
        }
        this.datepicker.on('datetime_changed', this, this.onInputChange.bind(this));
        this.datepicker.on('datetime_input', this, this.onInput.bind(this));
        this.datepicker.appendTo($(this.datepickerWrapperRef.el)).then(() => {
            this.datepickerInputEl = this.el.querySelector('.o_datepicker_input');
            this.datepickerInputEl.addEventListener('focusin', this.onInputFocusin.bind(this));
            this.datepickerInputEl.addEventListener('focusout', this.onInputFocusout.bind(this));
            if (this.props.value) {
                let val = moment.utc(this.props.value);
                if (this.props.isDatetime) {
                    val = val.utcOffset(-1 * (new Date().getTimezoneOffset())).format(DATETIME_FORMAT);
                    val = moment.utc(val);
                }
                this.datepicker.setValue(val);
            }
        });
    }

    getValue() {
        let tzOffset = new Date().getTimezoneOffset();
        let value = this.datepicker.getValue();
        if (this.props.isDatetime && !this.props.datetimeAsDate) {
            return !!value ? value.utcOffset(tzOffset).format(DATETIME_FORMAT) : false;
        } else {
            if (this.props.datetimeAsDate) {
                let fromValue = false;
                let toValue = false;
                if (!!value) {
                    let fromDate = value.set({ hour: 0, minute: 0, second: 0 });
                    let toDate = this.datepicker.getValue().set({ hour: 23, minute: 59, second: 59 });
                    fromValue = fromDate.utcOffset(tzOffset).format(DATETIME_FORMAT);
                    toValue = toDate.utcOffset(tzOffset).format(DATETIME_FORMAT);
                }
                if (this.props.type === INPUT_TYPE.FROM) {
                    return fromValue;
                } else if (this.props.type === INPUT_TYPE.TO) {
                    return toValue;
                } else {
                    return {
                        from: fromValue,
                        to: toValue,
                    };
                }
            } else {
                return !!value ? value.format(DATE_FORMAT) : false;
            }
        }
    }

    updateClearBtn() {
        this.state.showClearBtn = !!this.getValue();
    }

    onInputFocusin(event) {
        this.trigger('input-focusin');
    }

    onInputFocusout(event) {
        this.trigger('input-focusout');
    }

    onInputChange(event) {
        this.state.showClearBtn = !!this.getValue();
    }

    onInput(event) {
        if (!this.datepickerInputEl) {
            return;
        }
        this.state.showClearBtn = !!this.datepickerInputEl.value;
    }

    onClickClearBtn(event) {
        this.datepicker.setValue('');
        this.state.showClearBtn = false;
        this.trigger('clear-input', {
            inputType: this.props.type,
        });
    }
}

AdvancedSearchDatetimeFieldInput.props = {
    value: String,
    type: {
        type: String,
        validate: prop => Object.values(INPUT_TYPE).includes(prop),
    },
    isDatetime: {
        type: Boolean,
        optional: true,
    },
    datetimeAsDate: {
        type: Boolean,
        optional: true,
    },
};

AdvancedSearchDatetimeFieldInput.template = 'advanced_search_datetime_field_input';

class AdvancedSearchDatetimeField extends Component {
    constructor(...args) {
        super(...args);

        onMounted(this.onMounted.bind(this));

        this.INPUT_TYPE = INPUT_TYPE;
        this.isDatetime = this.props.field.type === DATETIME_FIELD;

        this.state= useState({
            showOptionsPanel: false,
            rangeSearch: checkFieldRangeMode(this.props.viewId, this.props.field.name),
            datetimeAsDate: this.isDatetime && checkFieldDatetimeAsDateMode(this.props.viewId, this.props.field.name),
        });

        this.searchQuery = this.getSearchQuery(this.props.searchModelState, this.props.field.name, this.getRangeSearchState());
    }

    onMounted() {
        this.optionsPanelHeight = this.getOptionsPanelHeight();
    }

    getRangeSearchState() {
        return this.state.rangeSearch || this.state.datetimeAsDate;
    }

    onClickSearchButton(event) {
        this.onSearch(this.getSearchValue('AdvancedSearchDatetimeFieldInput'));
    }

    onClickToggleDatetimeAsDateBtn(event) {
        if (this.isDatetime) {
            let newState = !this.state.datetimeAsDate;
            updateFieldDatetimeAsDateMode(this.props.viewId, this.props.field.name, newState);
            if (this.state.rangeSearch || this.state.datetimeAsDate) {
                this.onSearch({
                    from: false,
                    to: false,
                });
            } else {
                this.onSearch(false);
            }
            this.state.datetimeAsDate = newState;
            this.searchQuery = (this.state.rangeSearch || this.state.datetimeAsDate)
            ? { from: false, to: false }
            : false;
        }
    }

    onSearch(value) {
        let operator;
        if (!this.state.rangeSearch && !this.state.datetimeAsDate) {
            if (value === this.searchQuery) {
                return;
            }
            operator = '=';
        } else {
            if (value.from === this.searchQuery.from && value.to === this.searchQuery.to) {
                return;
            }
        }
        this.env.bus.trigger('advanced-search', {
            fieldType: this.props.field.type,
            fieldName: this.props.field.name,
            value,
            operator,
            fieldString: this.props.field.string,
        });
    }
}

patch(AdvancedSearchDatetimeField.prototype, 'AdvancedSearchDatetimeField_Mixin', AdvancedSearchMixinForFieldsWithRange);

AdvancedSearchDatetimeField.components = {
    AdvancedSearchDatetimeFieldInput,
};

AdvancedSearchDatetimeField.props = {
    field: {
        type: Object,
        validate: prop => [DATE_FIELD, DATETIME_FIELD].includes(prop.type),
    },
    attrs: Object,
    searchModelState: Object,
    viewId: Number,
};

AdvancedSearchDatetimeField.template = 'advanced_search_datetime_field';

export {
    AdvancedSearchDatetimeField,
}
