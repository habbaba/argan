/** @odoo-module **/

import { set_cookie, get_cookie } from 'web.utils';

const ADVANCED_LIST_SEARCH_CLASS = 'advanced_list_search';
const TEXT_FIELDS = ['char', 'text', 'html'];
const FLOAT_FIELDS = ['float', 'monetary']
const NUMERIC_FIELDS = ['integer', ...FLOAT_FIELDS]
const SIMPLE_FIELDS = [...TEXT_FIELDS, ...NUMERIC_FIELDS];
const SELECTION_FIELD = 'selection';
const RELATION_FIELDS = ['many2one', 'many2many'];
const DATE_FIELD = 'date';
const DATETIME_FIELD = 'datetime';
const STICKY_HEADER = {
	NONE: 'none',
	ALWAYS: 'always',
	ADVANCED_SEARCH : 'advanced_search',
}
const INPUT_TYPE = {
    SINGLE: 'single',
    FROM: 'from',
    TO: 'to',
};
const RANGE_KEY = 'range_search_fields_';
const DATETIME_AS_DATE_KEY = 'datetime_as_date_fields_';

function checkAdvancedListSearchClass(attrs) {
	if (attrs.class) {
		let classList = attrs.class.split(' ');
		return classList.includes(ADVANCED_LIST_SEARCH_CLASS);
	}
	return false;
}

function checkLocalStorage(key, field) {
	let fields = localStorage.getItem(key);
	if (fields) {
		try {
			fields = JSON.parse(fields);
		} catch (e) {
			return false;
		}
		return Array.isArray(fields) && fields.includes(field);
	}
	return false;
}

function updateLocalStorage(key, field, state) {
	let fields = localStorage.getItem(key);
	if (fields) {
		try {
			fields = JSON.parse(fields);
		} catch (e) {
			fields = [];
		}
	} else {
		fields = []
	}
	if (Array.isArray(fields)) {
		if (!fields.includes(field) && state) {
			fields.push(field);
		} else if (fields.includes(field) && !state) {
			fields.splice(fields.indexOf(field), 1);
		}
	} else {
		fields = [];
		if (state) {
			fields.push(field);
		}
	}
	localStorage.setItem(key, JSON.stringify(fields));
}

function checkFieldRangeMode(viewId, field) {
	const key = RANGE_KEY + viewId;
	return checkLocalStorage(key, field);
}

function updateFieldRangeMode(viewId, field, state) {
	const key = RANGE_KEY + viewId;
	updateLocalStorage(key, field, state);
}

function checkFieldDatetimeAsDateMode(viewId, field) {
	const key = DATETIME_AS_DATE_KEY + viewId;
	return checkLocalStorage(key, field);
}

function updateFieldDatetimeAsDateMode(viewId, field, state) {
	const key = DATETIME_AS_DATE_KEY + viewId;
	updateLocalStorage(key, field, state);
}

export {
	TEXT_FIELDS,
	FLOAT_FIELDS,
	NUMERIC_FIELDS,
	SIMPLE_FIELDS,
	SELECTION_FIELD,
	RELATION_FIELDS,
	DATE_FIELD,
	DATETIME_FIELD,
	INPUT_TYPE,
	STICKY_HEADER,
	checkAdvancedListSearchClass,
	checkFieldRangeMode,
	updateFieldRangeMode,
	checkFieldDatetimeAsDateMode,
	updateFieldDatetimeAsDateMode,
}
