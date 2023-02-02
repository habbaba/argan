/** @odoo-module **/

import AbstractController from 'web.AbstractController';

AbstractController.include({
	init: function (parent, model, renderer, params) {
		this._super.apply(this, arguments);
		this.viewId = params.viewId;
		this.isDialogView = false;
		if (parent.$parentNode) {
			this.isDialogView = parent.$parentNode[0].classList.contains('o_dialog_container');
		}
		this.setSearchModelViewType();
	},

	on_attach_callback: function () {
        this._super(...arguments);
		this.setSearchModelViewType();
    },

	setSearchModelViewType: function () {
		if (this.viewType !== 'form') {
			this.searchModel.dispatch('setViewInfo', {
				viewId: this.viewId,
				viewType: this.viewType,
				isDialogView: this.isDialogView,
			});
		}
	},
});
