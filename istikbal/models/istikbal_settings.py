from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
import json
import requests
import base64
import time
from datetime import datetime, timedelta


class Credentials(models.Model):
    _name = 'istikbal.credentials'

    username = fields.Char('Username')
    password = fields.Char('Password')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    active = fields.Boolean('Active',default=True)
