import json

from odoo import models, api


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super()._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if res.get('type', False) == 'tree':
            res['advanced_list_search_by_user'] = res.get('view_id') in self.env.user.advanced_list_search_view_ids.ids
            res['advanced_list_search_sticky_header'] = self.env['ir.config_parameter'].sudo()\
                .get_param('advanced_list_search.sticky_header', default='none')
        return res
