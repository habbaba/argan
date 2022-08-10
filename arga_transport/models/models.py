# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class arga_transport(models.Model):
#     _name = 'arga_transport.arga_transport'
#     _description = 'arga_transport.arga_transport'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
