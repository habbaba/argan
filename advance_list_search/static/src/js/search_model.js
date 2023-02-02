/** @odoo-module **/

import { SearchModel } from '@web/search/search_model';
import { patch } from 'web.utils';

patch(SearchModel.prototype, 'advanced_list_search/static/src/search_model.js', {
    getSearchItems(predicate) {
        let searchItems = this._super(...arguments);
        if (predicate && predicate.toString().includes('filter')) {
            searchItems = searchItems.filter(f => !f.advancedSearch);
        }
        return searchItems;
    },
});
