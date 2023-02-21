# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import json
import requests
import hashlib
from datetime import datetime


class InheritSO(models.Model):
    _inherit = 'sale.order'

    otto_order_id = fields.Char('OTTO Order ID')

