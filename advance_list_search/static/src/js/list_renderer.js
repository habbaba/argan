/** @odoo-module **/

import ListRenderer from 'web.ListRenderer';
import { AdvancedSearchTextField } from './advanced_search_text_field';
import { AdvancedSearchNumericField } from './advanced_search_numeric_field';
import { AdvancedSearchSelectionField } from './advanced_search_selection_field';
import { AdvancedSearchRelationField } from './advanced_search_relation_field';
import { AdvancedSearchDatetimeField } from './advanced_search_datetime_field';
import {
	STICKY_HEADER,
	TEXT_FIELDS,
	NUMERIC_FIELDS,
	SELECTION_FIELD,
	RELATION_FIELDS,
	DATE_FIELD,
	DATETIME_FIELD,
} from './main';
import 'web.EditableListRenderer';
import { ComponentWrapper } from 'web.OwlCompatibility';

ListRenderer.include({
	_renderView() {
		return this._super(...arguments).then(() => {
			if (this.state.count === 0 && !this.el.querySelector('table')) {
				let table = document.createElement('table');
				table.className = 'o_list_table table table-sm table-hover table-striped';
				table.appendChild(this._renderHeader()[0]);
				let tableWrapper = Object.assign(document.createElement('div'), {
					className: 'table-responsive',
				});
				tableWrapper.appendChild(table);
				this.el.appendChild(tableWrapper);
			}

			if (this.withStickyHeader() && this._shouldRenderOptionalColumnsDropdown()) {
                this.el.querySelector('div.o_optional_columns')?.remove();
                this.el.querySelector('thead').appendChild(this._renderOptionalColumnsDropdown()[0]);
            }
		});
	},

	_renderHeader: function (node) {
		let $thead = this._super(...arguments);
		let thead = $thead[0];
		if (this.withAdvancedSearch()) {
			thead.classList.add('advanced_list_search_thead');
			let tr = document.createElement('tr');

			if (this.hasSelectors) {
				tr.appendChild(document.createElement('th'));
			}

			for (let node of this.columns) {
				let th = document.createElement('th');
				tr.appendChild(th);
				let attrs = node.attrs || {};
				let fieldName = node.attrs.name;
				let field = this.state.fields[fieldName];

				if (!field || !field.searchable) {
					continue;
				}
				th.classList.add('advanced_search_th');

				let widget;
				if (TEXT_FIELDS.includes(field.type)) {
					widget = AdvancedSearchTextField;
				} else if (NUMERIC_FIELDS.includes(field.type)) {
					widget = AdvancedSearchNumericField;
				} else if (SELECTION_FIELD === field.type) {
					widget = AdvancedSearchSelectionField;
				} else if (RELATION_FIELDS.includes(field.type)) {
					widget = AdvancedSearchRelationField;
				} else if ([DATE_FIELD, DATETIME_FIELD].includes(field.type)) {
					widget = AdvancedSearchDatetimeField;
				}

				if (widget) {
					this.mountAdvancedSearchWidget({
						widget,
						target: th,
						field,
						attrs,
					});
				}
			}

			thead.appendChild(tr);
		}

		if (this.withStickyHeader()) {
			thead.classList.add('advanced_list_search_thead_sticky');
			if (this._shouldRenderOptionalColumnsDropdown()) {
				let optionalToggleEl = document.createElement('i');
				optionalToggleEl.className = 'o_optional_columns_dropdown_toggle fa fa-ellipsis-v';
				thead.appendChild(optionalToggleEl);
			}
		}

		return $thead;
	},

	mountAdvancedSearchWidget({ widget, target, field, attrs }) {
		let componentWrapper = new ComponentWrapper(this, widget, {
			field,
			attrs,
			searchModelState: this.searchModelState,
			viewId: this.viewId || 0,
		});
		componentWrapper.mount(target, {position: 'first-child'})
			.catch((e) => {
				console.log(e);
			});
	},

	setRowMode: function (recordID, mode) {
		let res = this._super(...arguments);
		if (this.withAdvancedSearch() && this.isEditable() && this.currentRow !== null) {
			this.currentRow = this.currentRow - 1;
		}
		return res;
	},

	_renderBody: function () {
		let res = this._super(...arguments);
		if (this.withAdvancedSearch() && this.isEditable() && this.currentRow !== null) {
			this.currentRow = this.currentRow - 1;
		}
		return res;
	},

	_selectCell: function (rowIndex, fieldIndex, options) {
		if (this.withAdvancedSearch() && this.isEditable() && rowIndex >= 0) {
			if (rowIndex === 0) {
				return;
			}
			rowIndex = rowIndex - 1;
		}
		return this._super(rowIndex, fieldIndex, options);
	},

	withAdvancedSearch: function () {
		return this.advancedSearchByCode || this.advancedSearchByUser;
	},

	withStickyHeader: function () {
		return this.advancedSearchStickyHeader === STICKY_HEADER.ALWAYS ||
			(this.advancedSearchStickyHeader === STICKY_HEADER.ADVANCED_SEARCH && this.withAdvancedSearch());
	}
});
