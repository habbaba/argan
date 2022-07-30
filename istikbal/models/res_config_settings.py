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



    def getCredentials(self):
        currentCompany = self.env.company
        istikbalCredentials = self.env['istikbal.credentials'].search([('company_id', '=', currentCompany.id),
                                                                       ('active', '=', True)])
        if len(istikbalCredentials.ids) > 1:
            raise ValidationError("Multiple Credentials are active for current company. Please select/active only one at a time.")
        elif len(istikbalCredentials.ids) == 0:
            raise ValidationError("No credential is assign to current company. Please go to Istikbal/Credentials.")
        else:
            return istikbalCredentials.username, istikbalCredentials.password

    def importInventory(self):
        username, password = self.getCredentials()
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
            odooProduct = self.env['product.template'].search([('name', '=', product['maktx'])])
            print( product['maktx'])
            if not odooProduct:
                new_product_template = self.env['product.template'].create({
                    'istikbal_product_code': product['producCode'],
                    'name': product['maktx'],
                    'packageNum':product['packageNum'],
                    'bdtCode':product['bdtCode'],
                    'productRef':product['productRef'],
                    'maktx':product['maktx'],
                    'vrkme':product['vrkme'],
                    'lgort':product['lgort'],
                    'volum': product['volum'],
                    'audat':product['audat'],
                    'stawn': product['stawn'],
                    'type': 'product',
                })
            else:
                odooProduct.write({
                    'istikbal_product_code': product['producCode'],
                    'name': product['maktx'],
                    'packageNum': product['packageNum'],
                    'bdtCode': product['bdtCode'],
                    'productRef': product['productRef'],
                    'maktx': product['maktx'],
                    'vrkme': product['vrkme'],
                    'lgort': product['lgort'],
                    'volum': product['volum'],
                    'audat': product['audat'],
                    'stawn': product['stawn'],
                    'type': 'product',
                })


    def importMaterials(self):
        username, password = self.getCredentials()
        odooProducts = self.env['product.template'].search([('default_code', '!=', False)],limit=500)
        allMaterials = []
        for odooProduct in odooProducts:
            url = "https://b2bapi.istikbal.com.tr/api/v1.0/data/getmaterial?materialNumber=" + odooProduct.default_code
            auth = str(base64.b64encode((str(username) + ':' + str(password)).encode()), 'utf-8')
            headers = {
                'Authorization': 'Basic ' + auth,
            }

            response = requests.request("GET", url, headers=headers)
            if response.status_code == 200:
                materials = json.loads(response.content)
                print(materials)
                if len(materials) > 0:
                    allMaterials.extend(materials)

        self.createMaterials(allMaterials)
        self.env.cr.commit()

    def createMaterials(self, materials):
        for material in materials:
            print(material)
            odooMaterials = self.env['istikbal.materials'].search([('materialNumber', '=', material['materialNumber'])])
            if not odooMaterials:
                odooMaterials = self.env['istikbal.materials'].create({
                    'materialNumber': material['materialNumber'],
                    'bdtModelName': material['bdtModelName'],
                    'bdtMaterialDesc': material['bdtMaterialDesc'],
                    'bdtEnglishMaterailDesc': material['bdtEnglishMaterailDesc'],
                    'netWeight': material['netWeight'],
                    'grossWeight': material['grossWeight'],
                    'numberExportContainer': material['numberExportContainer'],
                    'volum': material['volum'],
                    'producerCode': material['producerCode'],
                    'materialGroup': material['materialGroup'],
                })
            odooProduct = self.env['product.template'].search(
                [('istikbal_product_code', '=', material['materialNumber'])])
            if odooProduct:
                odooProduct.write({
                    'material_ids': [[4, odooMaterials.id]]
                })

    def importShipments(self):
        username, password = self.getCredentials()
        url = "https://b2bapi.istikbal.com.tr/api/v1.0/data/getshipments?getDetail=x"
        auth = str(base64.b64encode((str(username) + ':' + str(password)).encode()), 'utf-8')
        headers = {
            'Authorization': 'Basic ' + auth,
        }

        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            shipmentsHeader = json.loads(response.content)['getShipmentsHeader']
            shipmentsDetails = json.loads(response.content)['getShipmentsDetail']
            self.createShipmentsHeader(shipmentsHeader)
            self.createShipmentsDetails(shipmentsDetails)
            self.env.cr.commit()

    def createShipmentsHeader(self, headers):
        for header in headers:
            odooHeader = self.env['istikbal.shipments.header'].search([('shipmentNumber', '=', header['shipmentNumber'])])
            shipmentDate = datetime.strptime(header['shipmentDate'], '%Y-%m-%dT%H:%M:%S')
            if not odooHeader:
                self.env['istikbal.shipments.header'].create({
                    'containerNumber': header['containerNumber'],
                    'truckPlate': header['truckPlate'],
                    'truckPlate2': header['truckPlate2'],
                    'shipmentDate': shipmentDate,
                    'invoiceNumber': header['invoiceNumber'],
                    'shipmentNumber': header['shipmentNumber'],
                    'name': header['shipmentNumber'],
                    'volume': header['volume'],
                })
            else:
                odooHeader.write({
                    'containerNumber': header['containerNumber'],
                    'truckPlate': header['truckPlate'],
                    'truckPlate2': header['truckPlate2'],
                    'shipmentDate': shipmentDate,
                    'invoiceNumber': header['invoiceNumber'],
                    'shipmentNumber': header['shipmentNumber'],
                    'name': header['shipmentNumber'],
                    'volume': header['volume'],
                })

    def createShipmentsDetails(self, details):
        for detail in details:
            odooHeader = self.env['istikbal.shipments.header'].search([('shipmentNumber', '=', detail['shipmentNumber'])])
            odooDetails = self.env['istikbal.shipments.details'].search([('shipmentNumber', '=', detail['shipmentNumber']),
                                                                         ('packageNum', '=', detail['packageNum'])])
            if not odooDetails:
                self.env['istikbal.shipments.details'].create({
                    'shipment_id': odooHeader.id,
                    'packageNum': detail['packageNum'],
                    'shipmentNumber': detail['shipmentNumber'],
                    'bdtCode': detail['bdtCode'],
                    'productCode': detail['productCode'],
                    'productPackage': detail['productPackage'],
                    'quantity': detail['quantity'],
                    'orderReference': detail['orderReference'],
                    'bdtOrderNumber': detail['bdtOrderNumber'],
                    'customerItemReference': detail['customerItemReference'],
                    'customerItemCode': detail['customerItemCode'],
                    'customerOrderReference': detail['customerOrderReference'],
                    'productName': detail['productName'],
                    'productNamePack': detail['productNamePack'],
                    'productNameEN': detail['productNameEN'],
                    'volum': detail['volum'],
                    'zzbdtAmount': detail['zzbdtAmount'],
                })
