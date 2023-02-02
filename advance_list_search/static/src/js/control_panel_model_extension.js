/** @odoo-module **/

import ControlPanelModelExtension from 'web/static/src/js/control_panel/control_panel_model_extension.js';
import { patch } from 'web.utils';
import Domain from 'web.Domain';
import {
    SIMPLE_FIELDS,
    DATE_FIELD,
    DATETIME_FIELD,
} from "./main";

const DOMAIN_OPERATOR_DESCRIPTIONS = {
    'ilike': 'contains',
    '=': 'equals',
    '>=': '>=',
    '<=': '<=',
};

patch(ControlPanelModelExtension.prototype, 'advanced_list_search/static/src/control_panel_model_extension.js', {
    get(property, ...args) {
        if (property === 'state') {
            return this.state;
        }
        return this._super(...arguments);
    },

    _getFilters(predicate) {
        let filters = this._super(...arguments);
        if (predicate && predicate.toString().includes('filter')) {
            filters = filters.filter(f => !f.advancedSearch);
        }
        return filters;
    },

    _getFacets() {
        let facets = this._super();
        if (this.viewInfo?.viewType === 'list') {
            let advancedSearchFiltersGroupIds = Object.values(this.state.filters)
                .filter(f => !!f.advancedSearch && f.type === 'filter' && !!f.groupId)
                .map(f => f.groupId);
            facets = facets.filter(f => !advancedSearchFiltersGroupIds.includes(f.groupId));
        }
        return facets;
    },

    setViewInfo(viewInfo) {
        this.viewInfo = viewInfo;
    },

    async createNewFavorite(preFilter) {
        this._super(...arguments);
        this.env.bus.trigger('advanced-update-view', this.viewInfo);
    },

    addAdvancedFilterQuery({ fieldType, fieldName, operator, value, fieldString, valueDisplayName }) {
        let domain;
        let queryDescription;
        let fieldDescription = fieldString[0].toUpperCase() + fieldString.slice(1).toLowerCase();
        if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
            let domainArray = [];
            let queryDescriptionArray = [];
            if (value.from) {
                let operator = '>=';
                domainArray.push([fieldName, operator, value.from]);
                queryDescriptionArray.push(`${fieldDescription} is after "${value.from}"`);
            }
            if (value.to) {
                let operator = '<=';
                domainArray.push([fieldName, operator, value.to]);
                queryDescriptionArray.push(`${fieldDescription} is before "${value.to}"`);
            }
            if (domainArray.length) {
                domain = Domain.prototype.arrayToString(domainArray);
            }
            if (queryDescriptionArray.length > 1) {
                queryDescription = `${fieldDescription} is between "${value.from}" and "${value.to}"`;
            } else if (queryDescriptionArray.length === 1) {
                queryDescription = queryDescriptionArray[0];
            }
        } else if (value !== null) {
            domain = Domain.prototype.arrayToString([[fieldName, operator, value]]);
            let operatorDescription = DOMAIN_OPERATOR_DESCRIPTIONS[operator];
            let valueDescription = valueDisplayName || value;
            queryDescription = `${fieldDescription} ${operatorDescription} "${valueDescription}"`;
        }
        if (!domain) {
            value = false;
        }
        let filter;
        if ([...SIMPLE_FIELDS, DATE_FIELD, DATETIME_FIELD].includes(fieldType)) {
            filter = Object.values(this.state.filters)
                .find(f => f.type === 'filter' && !!f.advancedSearch && f.fieldName === fieldName);
        }
        if (!filter) {
            let existFieldFilter = Object.values(this.state.filters)
                .find(f => f.type === 'filter' && !!f.advancedSearch && f.fieldName === fieldName);
            let groupId;
            if (existFieldFilter) {
                groupId = existFieldFilter.groupId;
            } else {
                groupId = this.state.nextGroupId;
                this.state.nextGroupId++;
            }
            filter = {
                groupId,
                id: this.state.nextId,
                type: 'filter',
                fieldName,
                fieldType,
                advancedSearch: true,
            }
            if (valueDisplayName) {
                filter.valueDisplayName = valueDisplayName;
            }
            this.state.filters[this.state.nextId] = filter;
            this.state.nextId++;
        }
        let queryElement = this.state.query.find(f => f.filterId === filter.id);
        if (!queryElement) {
            filter.domain = domain;
            filter.description = queryDescription;
            this.state.query.push({
                groupId: filter.groupId,
                filterId: filter.id,
            });
        } else {
            if (!value) {
                this.state.query = this.state.query.filter(f => f.filterId !== filter.id);
                delete this.state.filters[filter.id];
            } else {
                filter.domain = domain;
                filter.description = queryDescription;
            }
        }
    },

    removeAdvancedSearchFilter(filterId) {
        if (this.state.filters[filterId]) {
            delete this.state.filters[filterId];
            this.state.query = this.state.query.filter(f => f.filterId !== filterId);
        }
    },

    removeAdvancedSearchFilterGroup(groupIds) {
        let filterIds = Object.values(this.state.filters)
            .filter(f => groupIds.includes(f.groupId) && !!f.advancedSearch).map(e => e.id);
        for (let id of filterIds) {
            delete this.state.filters[id];
        }
        this.state.query = this.state.query.filter(e => !filterIds.includes(e.filterId));
    },

    clearAdvancedSearchFilters() {
        let advancedSearchFilterIds = Object.values(this.state.filters)
            .filter(f => f.advancedSearch).map(f => f.id);
        this.state.query = this.state.query.filter(f => !advancedSearchFilterIds.includes(f.filterId));
    },
});
