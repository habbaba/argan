from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
import json
import requests
import base64
import time
from datetime import datetime, timedelta


class InheritPC(models.Model):
    _inherit = 'product.category'

    otto_category_group_id = fields.Many2one('otto.category.group', string='Category Group')
