/** @odoo-module **/

import FilterMenu from 'web.FilterMenu';
import { patch } from 'web.utils';
import { checkAdvancedListSearchClass } from './main';

const { useState } = owl.hooks;

patch(FilterMenu.prototype, 'advanced_list_search/static/src/filter_menu.js', {
    setup() {
        this.advancedSearchByCode = checkAdvancedListSearchClass(this.env.view?.arch.attrs);
        this.state = useState({
            advancedSearchByUser: !!this.env.view.advanced_list_search_by_user,
        });
    },

    onFilterSelected(ev) {
        let { itemId } = ev.detail.payload;
        if (itemId === 'toggleAdvancedListSearch') {
            if (!this.advancedSearchByCode && this.env.view.type === 'list') {
                let viewId = this.env.view.view_id;
                this.model.env.services.rpc({
                    model: 'res.users',
                    method: 'toggle_advanced_list_search_view_id',
                    args: [this.env.searchModel.config.context.uid],
                    kwargs: {
                        view_id: viewId,
                    },
                }).then((res) => {
                    if (res?.advanced_list_search !== undefined) {
                        this.state.advancedSearchByUser = res.advanced_list_search;
                        this.model.env.bus.trigger('clear_cache');
                        this.model.env.bus.trigger('update-advanced-search-state', {
                            advancedSearch: res.advanced_list_search,
                            viewId,
                        });
                        if (!this.state.advancedSearchByUser) {
                            this.env.searchModel.dispatch('clearAdvancedSearchFilters');
                        }
                    }
                });
            }
        } else {
            this._super(...arguments);
        }
    },
});
