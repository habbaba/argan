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

    image_url = fields.Char(string='Image URL')

    @api.onchange('image_url','default_code')
    def get_image_from_url(self):
        """This method mainly use to get image from the url"""
        image = False
        if self.image_url:
            if "http://" in self.image_url or "https://" in self.image_url:
                url = self.image_url + self.default_code
                filename = self.default_code + '.png'
                path = '/tmp/'
                BASE = 'https://mini.s-shot.ru/1024x0/JPEG/1024/Z100/?'
                url = urllib.parse.quote_plus(url) 
                response = requests.get(BASE + url, stream=True)
                if response.status_code == 200:
                    with open(path+filename, 'wb') as file:
                        for chunk in response:
                           file.write(chunk)
                    with open(path+filename, 'rb') as file:
                        image = base64.b64encode(file.read())
            else:
                if 'file:' in self.image_url:
                    with open(self.image_url.split("file:///")[1], 'rb') as file:
                        a = file.read()
                        print(type(a))
                        Image.save(a)
                        image = base64.b64encode(a)
                if '/home' in self.image_url:
                    with open(self.image_url, 'rb') as file:
                        image = base64.b64encode(file.read())
        self.image_1920 = image

    @api.model
    def create(self, values):
        res = super(ProductTemplateInherit, self).create(values)
        for img in res:
            if 'image_url' in values:
                img.get_image_from_url()
        return res

    def write(self, value):

        rec = super(ProductTemplateInherit, self).write(value)
        for img in self:  #
            if 'image_url' in value:
                img.get_image_from_url()
        return rec


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    image_url = fields.Char(string='Image URL')

    @api.onchange('image_url','default_code')
    def get_image_from_url(self):
        """This method mainly use to get image from the url"""
        image = img = False
        if self.image_url:
            if "http://" in self.image_url or "https://" in self.image_url:
                url = self.image_url + self.default_code
                filename = self.default_code + '.png'
                path = '/tmp/'
                BASE = 'https://mini.s-shot.ru/1024x0/JPEG/1024/Z100/?'
                url = urllib.parse.quote_plus(url) 
                response = requests.get(BASE + url, stream=True)
                if response.status_code == 200:
                    with open(path+filename, 'wb') as file:
                        for chunk in response:
                           file.write(chunk)
                    with open(path+filename, 'rb') as file:
                        image = base64.b64encode(file.read())
                
            else:
                if 'file' in self.image_url:
                    with open(self.image_url.split("file:///")[1], 'rb') as file:
                        image = base64.b64encode(file.read())
                if '/home' in self.image_url:
                    with open(self.image_url, 'rb') as file:
                        image = base64.b64encode(file.read())
        self.image_1920 = image

    @api.model
    def create(self, values):
        res = super(ProductProductInherit, self).create(values)
        for img in res:
            if 'image_url' in values:
                img.get_image_from_url()
        return res

    def write(self, value):
        rec = super(ProductProductInherit, self).write(value)
        for img in self:
            if 'image_url' in value:
                img.get_image_from_url()
        return rec
