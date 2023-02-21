from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
import json
import requests
import base64
import time
from datetime import datetime, timedelta


class OttoCategoryGroup(models.Model):
    _name = 'otto.category.group'
    _rec_name = 'otto_name'

    otto_name = fields.Char(string='Name')
