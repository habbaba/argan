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


    def importInventoryScheduler(self):

            istikbal_company = self.env['istikbal.credentials'].search([])
            for company in istikbal_company:
                try:
                    username = company.username
                    password = company.password
                    company_id = company.company_id.id
                    url = "https://b2bapi.istikbal.com.tr/api/v1.0/data/getinventory"
                    auth = str(base64.b64encode((str(username) + ':' + str(password)).encode()), 'utf-8')
                    headers = {
                        'Authorization': 'Basic ' + auth,
                    }
                    response = requests.request("GET", url, headers=headers)
                    if response.status_code == 200:
                        products = json.loads(response.content)
                        self.createIncomingShipmentScheduler(products,company_id)
                        self.env.cr.commit()
                    else:
                        log_notes = self.env["istikbal.log.notes"].sudo().create(
                            {"error": "shipments" + company.company_id.name + ": " + str(response.text)})
                except Exception as e:
                    log_notes = self.env["istikbal.log.notes"].sudo().create(
                        {"error": "importInventory" + company.company_id.name + ": " + str(e)})

    def createIncomingShipmentScheduler(self, products,company_id):
        for product in products:
            try:
                odooProduct = self.env['istikbal.incoming.shipments'].search([('producCode', '=', product['producCode']),('customerBarCode', '=', product['customerBarcode'])])
                if odooProduct:
                    odooProduct = self.env['istikbal.incoming.shipments'].write(
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
                         })

                else:
                    odooProduct = self.env['istikbal.incoming.shipments'].create(
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
                         'vrkme': product['vrkme'],
                         'lgort': product['lgort'],
                         'volum': product['volum'],
                         'audat': product['audat'],
                         'stawn': product['stawn'],
                         'company_id': company_id
                         })

            except Exception as e:
                log_notes = self.env["istikbal.log.notes"].sudo().create(
                    {"error": "CreateInventory" + str(e)})

    def importMaterialsScheduler(self):
        istikbal_company = self.env['istikbal.credentials'].search([])
        for company in istikbal_company:
            try:
                username = company.username
                password = company.password
                company_id = company.company_id.id
                odooProducts = self.env['product.template'].search([('default_code', '!=', False)])
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
                        log_notes = self.env["istikbal.log.notes"].sudo().create(
                            {"error": "shipments" + company.company_id.name + ": " + response})
                self.createMaterialsScheduler(allMaterials,company_id)
                self.env.cr.commit()
            except Exception as e:
                log_notes = self.env["istikbal.log.notes"].sudo().create(
                    {"error": "importInventory" + company.company_id.name + ": " + str(e)})


    def createMaterialsScheduler(self, materials,company_id):
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
                    'company_id': company_id,
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
                    'company_id':company_id,
                })
            odooProduct = self.env['product.template'].search(
                [('default_code', '=', material['materialNumber'])])
            if odooProduct:
                odooMaterials = self.env['istikbal.materials'].search(
                    [('materialNumber', '=', material['materialNumber'])])
                odooProduct.write({
                    'material_ids': [[4, odooMaterials.id]]
                })

    def importShipmentsScheduler(self):
        istikbal_company = self.env['istikbal.credentials'].search([])
        for company in istikbal_company:
            try:
                username = company.username
                password = company.password
                company_id = company.company_id.id
                url = "https://b2bapi.istikbal.com.tr/api/v1.0/data/getshipments?getDetail=x"
                auth = str(base64.b64encode((str(username) + ':' + str(password)).encode()), 'utf-8')
                headers = {
                    'Authorization': 'Basic ' + auth,
                }

                response = requests.request("GET", url, headers=headers)

                if response.status_code == 200:
                    shipmentsHeader = json.loads(response.content)['getShipmentsHeader']
                    shipmentsDetails = json.loads(response.content)['getShipmentsDetail']
                    self.createShipmentsHeaderScheduler(shipmentsHeader,shipmentsDetails,company_id)
                    self.env.cr.commit()
                else:
                    log_notes = self.env["istikbal.log.notes"].sudo().create(
                        {"error": "shipments" + company.company_id.name + ": " + response})
            except Exception as e:
                log_notes = self.env["istikbal.log.notes"].sudo().create(
                    {"error": "shipments" + company.company_id.name + ": " + response})


    def createShipmentsHeaderScheduler(self, headers,shipmentsDetails,company_id):
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
                    'company_id': company_id,
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
                    'company_id': company_id,
                })
        self.env.cr.commit()
        self.createShipmentsDetailsScheduler(shipmentsDetails,company_id)

    def createShipmentsDetailsScheduler(self, details,company_id):
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
                    'company_id': company_id,
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
                    'company_id': company_id,
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


