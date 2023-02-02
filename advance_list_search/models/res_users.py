from odoo import models, fields, Command


class ResUsers(models.Model):
    _inherit = 'res.users'

    advanced_list_search_view_ids = fields.Many2many('ir.ui.view')

    def toggle_advanced_list_search_view_id(self, view_id):
        self.ensure_one()
        view = self.env['ir.ui.view'].sudo().browse(view_id).exists()
        if view:
            if view.id not in self.sudo().advanced_list_search_view_ids.ids:
                self.sudo().advanced_list_search_view_ids = [Command.link(view.id)]
            else:
                self.sudo().advanced_list_search_view_ids = [Command.unlink(view.id)]
        return {
            'advanced_list_search': view.id in self.sudo().advanced_list_search_view_ids.ids,
        }
