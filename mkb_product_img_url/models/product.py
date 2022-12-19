# -*- coding: utf-8 -*-
# Copyright 2020-21 Manish Kumar Bohra <manishkumarbohra@outlook.com> or <manishbohra1994@gmail.com>
# License LGPL-3 - See http://www.gnu.org/licenses/Lgpl-3.0.html
from odoo import models, fields, api,_
import requests
import base64
import requests
import urllib.parse

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    image_url = fields.Char(string='Image URL',compute="compute_the_image_url")


    def compute_the_image_url(self):
        for i in self:
            i.image_url='https://sapservices.boydak.net/fabric/material/'+i.default_code


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    image_url = fields.Char(string='Image URL', compute="compute_the_image_url")

    def compute_the_image_url(self):
        for i in self:
            i.image_url = 'https://sapservices.boydak.net/fabric/material/' + i.default_code