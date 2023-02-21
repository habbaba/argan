# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import json
import requests
import hashlib
from datetime import datetime


class InheritPT(models.Model):
    _inherit = 'product.template'

    otto_brand_id = fields.Many2one('otto.brand', string='Product Brand')

