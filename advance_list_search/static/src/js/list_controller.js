/** @odoo-module **/

import ListController from 'web.ListController';
import env from 'web.env';

ListController.include({
	init: function (parent, model, renderer, params) {
		this._super.apply(this, arguments);
		this.setRendererSearchModelState();
		this.renderer.viewId = this.viewId;
		this.renderer.advancedSearchByCode = params.advancedSearchByCode;
		this.renderer.advancedSearchByUser = params.advancedSearchByUser;
		this.renderer.advancedSearchStickyHeader = params.advancedSearchStickyHeader;
	},

	start: async function (parent, model, renderer, params) {
        env.bus.on('update-advanced-search-state', null, this.updateAdvancedSearchState.bind(this));
		env.bus.on('advanced-search', null, this.onAdvancedSearch.bind(this));
		env.bus.on('advanced-search-remove-filter', null, this.onAdvancedSearchRemoveFilter.bind(this));
		env.bus.on('advanced-search-remove-filter-group', null, this.onAdvancedSearchRemoveFilterGroup.bind(this));
		env.bus.on('advanced-update-view', null, this.onAdvancedUpdate.bind(this));
        await this._super(...arguments);
    },

	update: function (params, options) {
		this.setRendererSearchModelState();
		return this._super.apply(this, arguments);
	},

	setRendererSearchModelState: function () {
		this.renderer.searchModelState = this.searchModel.get('state');
	},

	onAdvancedSearch(data) {
        this.searchModel.dispatch('addAdvancedFilterQuery', data);
    },

	onAdvancedSearchRemoveFilter(data) {
        this.searchModel.dispatch('removeAdvancedSearchFilter', data);
    },

	onAdvancedSearchRemoveFilterGroup(data) {
        this.searchModel.dispatch('removeAdvancedSearchFilterGroup', data);
    },

	onAdvancedUpdate(viewInfo) {
		if (this.viewId === viewInfo.viewId) {
			this.reload();
		}
	},

	updateAdvancedSearchState: function (data) {
		if (data.viewId === this.viewId) {
			this.renderer.advancedSearchByUser = data.advancedSearch;
			this._updateRendererState();
		}
	},
});
