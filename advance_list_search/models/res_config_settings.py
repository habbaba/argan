from ast import literal_eval

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    list_view_sticky_header = fields.Selection(
        selection=[
            ('none', 'None'),
            ('always', 'Always'),
            ('advanced_search', 'Only with advanced search'),
        ],
        default='none',
        required=True,
        config_parameter='advanced_list_search.sticky_header')
