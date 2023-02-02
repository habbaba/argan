/** @odoo-module **/

import ListView from 'web.ListView';
import { checkAdvancedListSearchClass } from './main';

ListView.include({
	init: function (viewInfo, params) {
		this._super(...arguments);
		this.controllerParams.advancedSearchByCode = checkAdvancedListSearchClass(this.arch.attrs);
		this.controllerParams.advancedSearchByUser = viewInfo.advanced_list_search_by_user;
		this.controllerParams.advancedSearchStickyHeader = viewInfo.advanced_list_search_sticky_header;
	},
});
