# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import json
from datetime import datetime


class InheritPT(models.Model):
    _inherit = 'product.template'

    istikbal_product_code = fields.Char('Product Code')
    syncedIstikbal = fields.Boolean('Synced Istikbal', default=False)

