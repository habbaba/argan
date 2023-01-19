# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class remove_view_order(models.Model):
#     _name = 'remove_view_order.remove_view_order'
#     _description = 'remove_view_order.remove_view_order'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
