from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
import json
import requests
import base64
import time
from datetime import datetime, timedelta

INTERVAL = [
    ('minutes', 'Minutes'),
    ('hours', 'Hours'),
    ('days', 'Days'),
    ('weeks', 'Weeks'),
    ('months', 'Months')
]


class Integration(models.TransientModel):
    _inherit = 'res.config.settings'

    username = fields.Char('Username')
    password = fields.Char('Password')
    importInventoryButton = fields.Boolean("Import Inventory")
    importInventoryUnit = fields.Integer("Import Unit")
    importInventoryInterval = fields.Selection(INTERVAL, "Import Interval", default='months')

    def TurnOnAndOffSchedulers(self):
        if self.exportInvoicesButton:
            self.changeSettingsOfExportInvoicesScheduler(True)

        if not self.exportInvoicesButton:
            self.changeSettingsOfExportInvoicesScheduler(False)

    def changeSettingsOfExportInvoicesScheduler(self, state):
        scheduler = self.env['ir.cron'].search([('name', '=', 'Export Odoo Invoices/Bills')])
        if not scheduler:
            scheduler = self.env['ir.cron'].search([('name', '=', 'Export Odoo Invoices/Bills'),
                                                    ('active', '=', False)])
        scheduler.active = state
        scheduler.interval_number = self.exportInvoicesUnit
        scheduler.interval_type = self.exportInvoicesInterval

    def set_values(self):
        res = super(Integration, self).set_values()
        self.env['ir.config_parameter'].set_param('istikbal.username', self.username)
        self.env['ir.config_parameter'].set_param('istikbal.password', self.password)

        return res

    @api.model
    def get_values(self):
        res = super(Integration, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        username = IrConfigParameter.get_param('istikbal.username')
        password = IrConfigParameter.get_param('istikbal.password')

        res.update(
            username=username,
            password=password,
        )

        return res

    def importInventory(self):
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        username = IrConfigParameter.get_param('istikbal.username')
        password = IrConfigParameter.get_param('istikbal.password')
        url = "https://b2bapi.istikbal.com.tr/api/v1.0/data/getinventory"
        auth = str(base64.b64encode((str(username) + ':' + str(password)).encode()), 'utf-8')
        headers = {
            'Authorization': 'Basic ' + auth,
        }

        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            products = json.loads(response.content)
            self.createProducts(products)
            self.env.cr.commit()

    def createProducts(self, products):
        for product in products:
            odooProduct = self.env['product.template'].search([('default_code', '=', product['producCode'])])
            if odooProduct:
                new_product_template = self.env['product.template'].write({
                    'default_code': product['producCode'],
                    'name': product['maktx'],
                    'bdtCode': product['bdtCode'],
                    'quantity': product['quantity'],
                    'customerRef': product['customerRef'],
                    'productRef': product['productRef'],
                    'customerBarcode': product['customerBarcode'],
                    'packageNum': product['packageNum'],
                    'vrkme': product['vrkme'],
                    'lgort': product['lgort'],
                    'volum': product['volum'],
                    'audat': product['audat'],
                    'stawn': product['stawn'],
                    'description': product['text'],
                    'type': 'product'
                })
            else:
                new_product_template = self.env['product.template'].create({
                    'default_code': product['producCode'],
                    'name': product['maktx'],
                    'bdtCode': product['bdtCode'],
                    'quantity': product['quantity'],
                    'customerRef': product['customerRef'],
                    'productRef': product['productRef'],
                    'customerBarcode': product['customerBarcode'],
                    'packageNum': product['packageNum'],
                    'vrkme': product['vrkme'],
                    'lgort': product['lgort'],
                    'volum': product['volum'],
                    'audat': product['audat'],
                    'stawn': product['stawn'],
                    'description': product['text'],
                    'type': 'product'
                })