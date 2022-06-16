# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import json
from datetime import datetime


class InheritPT(models.Model):
    _inherit = 'product.template'

    istikbal_product_code = fields.Char('Product Code')
    bdtCode = fields.Char('BdtCode')
    quantity = fields.Float('Quantity')
    customerRef = fields.Char('CustomerRef')
    productRef = fields.Char('ProductRef')
    customerBarcode = fields.Char('CustomerBarcode')
    packageNum = fields.Char('PackageNum')
    vrkme = fields.Char('Vrkme')
    lgort = fields.Float('Lgort')
    volum = fields.Float('Volum')
    audat = fields.Char('Audat')
    stawn = fields.Char('Stawn')
    syncedIstikbal = fields.Boolean('Synced Istikbal', default=False)