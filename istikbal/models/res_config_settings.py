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

    importMaterialsButton = fields.Boolean("Import Materials")
    importMaterialsUnit = fields.Integer("Import Unit")
    importMaterialsInterval = fields.Selection(INTERVAL, "Import Materials", default='months')

    importShipmentsButton = fields.Boolean("Import Shipments")
    importShipmentsUnit = fields.Integer("Import Unit")
    importShipmentsInterval = fields.Selection(INTERVAL, "Import Shipments", default='months')

    def TurnOnAndOffSchedulers(self):
        if self.importInventoryButton:
            self.changeSettingsOfImportInventoryScheduler(True)

        if not self.importInventoryButton:
            self.changeSettingsOfImportInventoryScheduler(False)

        if self.importMaterialsButton:
            self.changeSettingsOfImportMaterialsScheduler(True)

        if not self.importMaterialsButton:
            self.changeSettingsOfImportMaterialsScheduler(False)

        if self.importShipmentsButton:
            self.changeSettingsOfImportShipmentsScheduler(True)

        if not self.importShipmentsButton:
            self.changeSettingsOfImportShipmentsScheduler(False)

    def changeSettingsOfImportInventoryScheduler(self, state):
        scheduler = self.env['ir.cron'].search([('name', '=', 'Import Inventory')])
        if not scheduler:
            scheduler = self.env['ir.cron'].search([('name', '=', 'Import Inventory'),
                                                    ('active', '=', False)])
        scheduler.active = state
        scheduler.interval_number = self.importInventoryUnit
        scheduler.interval_type = self.importInventoryInterval

    def changeSettingsOfImportMaterialsScheduler(self, state):
        scheduler = self.env['ir.cron'].search([('name', '=', 'Import Materials')])
        if not scheduler:
            scheduler = self.env['ir.cron'].search([('name', '=', 'Import Materials'),
                                                    ('active', '=', False)])
        scheduler.active = state
        scheduler.interval_number = self.importMaterialsUnit
        scheduler.interval_type = self.importMaterialsInterval

    def changeSettingsOfImportShipmentsScheduler(self, state):
        scheduler = self.env['ir.cron'].search([('name', '=', 'Import Shipments')])
        if not scheduler:
            scheduler = self.env['ir.cron'].search([('name', '=', 'Import Shipments'),
                                                    ('active', '=', False)])
        scheduler.active = state
        scheduler.interval_number = self.importShipmentsUnit
        scheduler.interval_type = self.importShipmentsInterval

    def set_values(self):
        res = super(Integration, self).set_values()
        self.env['ir.config_parameter'].set_param('istikbal.importInventoryButton', self.importInventoryButton)
        self.env['ir.config_parameter'].set_param('istikbal.importInventoryUnit', self.importInventoryUnit)
        self.env['ir.config_parameter'].set_param('istikbal.importInventoryInterval', self.importInventoryInterval)
        self.env['ir.config_parameter'].set_param('istikbal.importMaterialsButton', self.importMaterialsButton)
        self.env['ir.config_parameter'].set_param('istikbal.importMaterialsUnit', self.importMaterialsUnit)
        self.env['ir.config_parameter'].set_param('istikbal.importMaterialsInterval', self.importMaterialsInterval)
        self.env['ir.config_parameter'].set_param('istikbal.importShipmentsButton', self.importShipmentsButton)
        self.env['ir.config_parameter'].set_param('istikbal.importShipmentsUnit', self.importShipmentsUnit)
        self.env['ir.config_parameter'].set_param('istikbal.importShipmentsInterval', self.importShipmentsInterval)

        self.TurnOnAndOffSchedulers()
        return res

    @api.model
    def get_values(self):
        res = super(Integration, self).get_values()
        icpsudo = self.env['ir.config_parameter'].sudo()
        importInventoryButton = icpsudo.get_param('istikbal.importInventoryButton')
        importInventoryUnit = icpsudo.get_param('istikbal.importInventoryUnit')
        importInventoryInterval = icpsudo.get_param('istikbal.importInventoryInterval')
        importMaterialsButton = icpsudo.get_param('istikbal.importMaterialsButton')
        importMaterialsUnit = icpsudo.get_param('istikbal.importMaterialsUnit')
        importMaterialsInterval = icpsudo.get_param('istikbal.importMaterialsInterval')
        importShipmentsButton = icpsudo.get_param('istikbal.importShipmentsButton')
        importShipmentsUnit = icpsudo.get_param('istikbal.importShipmentsUnit')
        importShipmentsInterval = icpsudo.get_param('istikbal.importShipmentsInterval')

        res.update(
            importInventoryButton=True if importInventoryButton == 'True' else False,
            importMaterialsButton=True if importMaterialsButton == 'True' else False,
            importShipmentsButton=True if importShipmentsButton == 'True' else False,
            importInventoryUnit=importInventoryUnit,
            importInventoryInterval=importInventoryInterval,
            importMaterialsUnit=importMaterialsUnit,
            importMaterialsInterval=importMaterialsInterval,
            importShipmentsUnit=importShipmentsUnit,
            importShipmentsInterval=importShipmentsInterval,
        )
        return res


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
        try:
            username, password = self.getCredentials()
            url = "https://b2bapi.istikbal.com.tr/api/v1.0/data/getinventory"
            auth = str(base64.b64encode((str(username) + ':' + str(password)).encode()), 'utf-8')
            headers = {
                'Authorization': 'Basic ' + auth,
            }
            response = requests.request("GET", url, headers=headers)
            print(response, response.content)
            if response.status_code == 200:
                products = json.loads(response.content)
                self.createIncomingShipment(products)
                self.env.cr.commit()
        except Exception as e:
            if "Connection aborted" in str(e):
                time.sleep(60)
                self.importInventory()

    def createIncomingShipment(self, products):
        for product in products:
            odooProduct = self.env['istikbal.incoming.shipments'].search([('producCode', '=', product['producCode'])])
            if odooProduct:
                incoming_shipment = self.env['istikbal.incoming.shipments'].write(
                    {
                     'bdtCode': product['bdtCode'],
                      'customerBarCode': product['customerBarcode'],
                     'producCode': product['producCode'],
                     'quantity': product['quantity'],
                     'customerRef': product['customerRef'],
                     'productRef': product['productRef'],
                     'text': product['text'],
                     'packageEnum': product['packageNum'],
                     'maktx': product['maktx'],
                     'vrkme':product['vrkme'],
                     'lgort': product['lgort'],
                     'volum': product['volum'],
                     'audat': product['audat'],
                     'stawn': product['stawn'],
                     'company_id':self.env.company.id
                     })

            else:
                incoming_shipment = self.env['istikbal.incoming.shipments'].create(
                    {
                   
                      'customerBarCode': product['customerBarcode'],
                     'producCode': product['producCode'],
                     'quantity': product['quantity'],
                     'customerRef': product['customerRef'],
                     'productRef': product['productRef'],
                     'text': product['text'],
                     'packageEnum': product['packageNum'],
                     'maktx': product['maktx'],
                     'vrkme': product['vrkme'],
                     'lgort': product['lgort'],
                     'volum': product['volum'],
                     'audat': product['audat'],
                     'stawn': product['stawn'],
                     'company_id': self.env.company.id
                     })



    def importMaterials(self):
        try:
            username, password = self.getCredentials()
            odooProducts = self.env['product.template'].search([('default_code', '!=', False)],limit=500)
            allMaterials = []
            for odooProduct in odooProducts:
                url = "https://b2bapi.istikbal.com.tr/api/v1.0/data/getmaterial?materialNumber=" + odooProduct.default_code
                auth = str(base64.b64encode((str(username) + ':' + str(password)).encode()), 'utf-8')
                headers = {
                    'Authorization': 'Basic ' + auth,
                }
                response = requests.request("GET", url, headers=headers,timeout=60)
                if response.status_code == 200:
                    materials = json.loads(response.content)
                    if len(materials) > 0:
                        allMaterials.extend(materials)
                else:
                    raise ValidationError("Error.", response)
            self.createMaterials(allMaterials)
            self.env.cr.commit()
        except Exception as e:
            if "Connection aborted" in str(e):
                time.sleep(60)
                self.importMaterials()

    def createMaterials(self, materials):
        for material in materials:
            odooMaterials = self.env['istikbal.materials'].search([('materialNumber', '=', material['materialNumber'])])
            if odooMaterials:
                odooMaterials = self.env['istikbal.materials'].write({
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
                    'vmstd':material['vmstd'],
                    'vmsta':material['vmsta'],
                    'bdtKartela':material['bdtKartela'],
                    'meins':material['meins'],
                    'ersda':material['ersda'],
                    'productClass':material['productClass'],
                    'productClassDef': material['productClassDef'],
                    'mtpos': material['mtpos'],
                    'prodh': material['prodh'],
                    'vtext': material['vtext'],
                    'mvgr3': material['mvgr3'],
                    'zzbolG01': material['zzbolG01'],
                    'zzbolG02': material['zzbolG02'],
                    'zzbolG03': material['zzbolG03'],
                    'zzbolG04': material['zzbolG04'],
                    'zzbolG05': material['zzbolG05'],
                    'zzbolG06': material['zzbolG06'],
                    'zzbolG07': material['zzbolG07'],
                    'zzbolG08': material['zzbolG08'],
                    'zzbolG09': material['zzbolG09'],
                    'zzbolG10': material['zzbolG10'],
                    'zzbolG11': material['zzbolG11'],
                    'zzbolG12': material['zzbolG12'],
                    'zzbolG13': material['zzbolG13'],
                    'zzbolG14': material['zzbolG14'],
                    'zzbolG15': material['zzbolG15'],
                    'fabric': material['fabric'],
                    'company_id': self.env.company.id,
                })
            else:
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
                    'vmstd': material['vmstd'],
                    'vmsta': material['vmsta'],
                    'bdtKartela': material['bdtKartela'],
                    'meins': material['meins'],
                    'ersda': material['ersda'],
                    'productClass': material['productClass'],
                    'productClassDef': material['productClassDef'],
                    'mtpos': material['mtpos'],
                    'prodh': material['prodh'],
                    'vtext': material['vtext'],
                    'mvgr3': material['mvgr3'],
                    'zzbolG01': material['zzbolG01'],
                    'zzbolG02': material['zzbolG02'],
                    'zzbolG03': material['zzbolG03'],
                    'zzbolG04': material['zzbolG04'],
                    'zzbolG05': material['zzbolG05'],
                    'zzbolG06': material['zzbolG06'],
                    'zzbolG07': material['zzbolG07'],
                    'zzbolG08': material['zzbolG08'],
                    'zzbolG09': material['zzbolG09'],
                    'zzbolG10': material['zzbolG10'],
                    'zzbolG11': material['zzbolG11'],
                    'zzbolG12': material['zzbolG12'],
                    'zzbolG13': material['zzbolG13'],
                    'zzbolG14': material['zzbolG14'],
                    'zzbolG15': material['zzbolG15'],
                    'fabric': material['fabric'],
                    'company_id': self.env.company.id,
                })
            odooProduct = self.env['product.template'].search(
                [('default_code', '=', material['materialNumber'])])
            if odooProduct:
                odooMaterials = self.env['istikbal.materials'].search(
                    [('materialNumber', '=', material['materialNumber'])])
                odooProduct.write({
                    'material_ids': [[4, odooMaterials.id]]
                })

    def importShipments(self):
        try:
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
                self.createShipmentsHeader(shipmentsHeader,shipmentsDetails)
                self.env.cr.commit()
        except Exception as e:
            if "Connection aborted" in str(e):
                time.sleep(60)
                self.importShipments()


    def createShipmentsHeader(self, headers,shipmentsDetails):
        for header in headers:
            odooHeader = self.env['istikbal.shipments.header'].search([('shipmentNumber', '=', header['shipmentNumber'])])
            shipmentDate = datetime.strptime(header['shipmentDate'], '%Y-%m-%dT%H:%M:%S')
            if not odooHeader:
                self.env['istikbal.shipments.header'].create({
                    'disPactDate': header['dispatchDate'],
                    'containerNumber': header['containerNumber'],
                    'truckPlate': header['truckPlate'],
                    'shipmentDate': shipmentDate,
                    'truckPlate2': header['truckPlate2'],
                    'invoiceNumber': header['invoiceNumber'],
                    'shipmentNumber': header['shipmentNumber'],
                    'volum': header['volume'],
                    'voleh': header['volume'],
                    'company_id': self.env.company.id,
                })

            else:
                odooHeader.write({
                    'disPactDate': header['dispatchDate'],
                    'containerNumber': header['containerNumber'],
                    'truckPlate': header['truckPlate'],
                    'shipmentDate': shipmentDate,
                    'truckPlate2': header['truckPlate2'],
                    'invoiceNumber': header['invoiceNumber'],
                    'shipmentNumber': header['shipmentNumber'],
                    'volum': header['volume'],
                    'voleh': header['volume'],
                    'company_id': self.env.company.id,
                })
        self.env.cr.commit()
        self.createShipmentsDetails(shipmentsDetails)

    def createShipmentsDetails(self, details):
        for detail in details:
            odooHeader = self.env['istikbal.shipments.header'].search([('shipmentNumber', '=', detail['shipmentNumber'])],limit=1)
            odooDetails = self.env['istikbal.shipments.details'].search([('shipMentNumber', '=', detail['shipmentNumber']), ('pakageEnum', '=', detail['packageNum'])],limit=1)

            if odooDetails:
                odooDetails=self.env['istikbal.shipments.details'].write({
                    'shipment_id': odooHeader.id,
                    'pakageEnum': detail['packageNum'],
                    'shipMentNumber': detail['shipmentNumber'],
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
                    'vrkme': detail['vrkme'],
                    'inhalt': detail['inhalt'],
                    'mvgr3Desc': detail['mvgr3Desc'],
                    'brgew': detail['brgew'],
                    'gewei': detail['gewei'],
                    'voleh': detail['voleh'],
                    'company_id': self.env.company.id,
                })

            else:
                odooDetails = self.env['istikbal.shipments.details'].create({
                    'shipment_id': odooHeader.id,
                    'pakageEnum': detail['packageNum'],
                    'shipMentNumber': detail['shipmentNumber'],
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
                    'vrkme': detail['vrkme'],
                    'inhalt': detail['inhalt'],
                    'mvgr3Desc': detail['mvgr3Desc'],
                    'brgew': detail['brgew'],
                    'gewei': detail['gewei'],
                    'voleh': detail['voleh'],
                    'company_id': self.env.company.id,
                })

    def importSaleOrderAnalysis(self):
        username, password = self.getCredentials()
        url = "https://b2bapi.istikbal.com.tr/api/v1.0/data/getordersanalysisreport?dudDate=" + "01.07.2022"+"&"+"dddateb="+"01.08.2022"
        auth = str(base64.b64encode((str(username) + ':' + str(password)).encode()), 'utf-8')
        headers = {
            'Authorization': 'Basic ' + auth,
        }

        response = requests.request("GET", url, headers=headers)
        print(response.text)
            # if response.status_code == 200:
            #     materials = json.loads(response.content)


