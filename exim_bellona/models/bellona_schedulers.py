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



    def getBaseURL(self):
        return "https://eximapi.bellona.com.tr/"

    # Beloona Shipments
    def importBellonaInventoryScheduler(self):
        bellona_company = self.env['bellona.credentials'].search([])
        for company in bellona_company:
            token = company.token
            company_id = company.company_id.id
            url = self.getBaseURL() + "api/Material/SearchInventory"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token,
            }
            payload = json.dumps(False)
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                shipments = json.loads(response.content)
                self.createShipmentsScheduler(shipments,company_id)
                self.env.cr.commit()
            else:
                log_notes = self.env["bellona.log.notes"].sudo().create(
                    {"error": token+"shipment"+company.company_id.name + ": " + str(response)})

    def createShipmentsScheduler(self, shipments,company_id):
        for shipment in shipments:
            shipment_obj = self.env['bellona.shipments'].search([('saleS_ORDER', '=', shipment['saleS_ORDER']), (
            'saleS_ORDER_POSNR', '=', shipment['saleS_ORDER_POSNR']), ('productref', '=', shipment['productref']),
                                                                 ('company_id', '=', company_id)])
            product_template = self.env['product.template'].search(
                [('default_code', '=', shipment['productcode']), ('company_id', '=', company_id)], limit=1)
            if not shipment_obj:
                shipment_obj = self.env['bellona.shipments'].sudo().create({
                    'productcode': shipment['productcode'],
                    'product_template': product_template.id,
                    'ordeR_QUANTITY': shipment['ordeR_QUANTITY'],
                    'stocK_QUANTITY': shipment['stocK_QUANTITY'],
                    'customerref': shipment['customerref'],
                    'productref': shipment['productref'],
                    'packagenum': shipment['packagenum'],
                    'maktX_TR': shipment['maktX_TR'],
                    'maktX_EN': shipment['maktX_EN'],
                    'volum': shipment['volum'],
                    'audat': shipment['audat'],
                    'stawn': shipment['stawn'],
                    'saleS_ORDER': shipment['saleS_ORDER'],
                    'saleS_ORDER_POSNR': shipment['saleS_ORDER_POSNR'],
                    'balancE_QUANTITY': shipment['balancE_QUANTITY'],
                    'materiaL_TEXT': shipment['materiaL_TEXT'],
                    'previouS_ORDER': shipment['previouS_ORDER'],
                    'materiaL_VOLUM': shipment['materiaL_VOLUM'],
                    'customerbarcode': shipment['customerbarcode'],
                    'previouS_ORDER_POS': shipment['previouS_ORDER_POS'],
                    'producT_STOCK': shipment['producT_STOCK'],
                    'company_id':company_id
                })

            else:
                shipment_obj = self.env['bellona.shipments'].write({
                    'productcode': shipment['productcode'],
                    'product_template': product_template.id,
                    'ordeR_QUANTITY': shipment['ordeR_QUANTITY'],
                    'stocK_QUANTITY': shipment['stocK_QUANTITY'],
                    'customerref': shipment['customerref'],
                    'productref': shipment['productref'],
                    'packagenum': shipment['packagenum'],
                    'maktX_TR': shipment['maktX_TR'],
                    'maktX_EN': shipment['maktX_EN'],
                    'volum': shipment['volum'],
                    'audat': shipment['audat'],
                    'stawn': shipment['stawn'],
                    'saleS_ORDER': shipment['saleS_ORDER'],
                    'saleS_ORDER_POSNR': shipment['saleS_ORDER_POSNR'],
                    'balancE_QUANTITY': shipment['balancE_QUANTITY'],
                    'materiaL_TEXT': shipment['materiaL_TEXT'],
                    'previouS_ORDER': shipment['previouS_ORDER'],
                    'materiaL_VOLUM': shipment['materiaL_VOLUM'],
                    'customerbarcode': shipment['customerbarcode'],
                    'previouS_ORDER_POS': shipment['previouS_ORDER_POS'],
                    'producT_STOCK': shipment['producT_STOCK'],
                })

            purchase_order = self.env['purchase.order'].search([('name', '=', shipment['customerbarcode'])], limit=1)
            if purchase_order:
                sale_order = self.env['sale.order'].search([('name', '=', purchase_order.origin)], limit=1)
                purchase_order.bellona_shipments = [(4, shipment_obj.id)]
                if sale_order:
                    sale_order.bellona_shipments = [(4, shipment_obj.id)]

    # Bellona Materials
    def importBellonaMaterialsScheduler(self):

        bellona_company = self.env['bellona.credentials'].search([])
        for company in bellona_company:
            token = company.token
            company_id = company.company_id.id
            url = self.getBaseURL() + "api/Material/SearchMaterial"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token,
            }
            odooProducts = self.env['product.template'].search([('default_code', '!=', False), ('company_id', '=', company_id),
                 ("bellona_material_ids", '=', False)],limit=1)

            for odooProduct in odooProducts:

                data = {
                    "matnr": odooProduct.default_code,
                    "date": "2022-07-01"
                }
                payload = json.dumps(data)
                response = requests.request("POST", url, headers=headers, data=payload)

                if response.status_code == 200:
                    products = json.loads(response.content)
                    self.createBellonaMaterialsScheduler(products,company_id)
                else:
                    log_notes = self.env["bellona.log.notes"].sudo().create(
                        {"error": "Material"+company.company_id.name + ": " + str(response.text)})

            self.env.cr.commit()

    def createBellonaMaterialsScheduler(self, materials,company_id):
        for material in materials:
            odooMaterials = self.env['bellona.material'].search(
                [('matnr', '=', material['matnr']), ('company_id', '=', company_id)],limit=1)
            odooProduct = self.env['product.template'].search(
                [('default_code', '=', material['matnr']), ('company_id', '=', company_id)], limit=1)
            if not odooMaterials:
                odooMaterials = self.env['bellona.material'].sudo().create({
                    'matnr': material['matnr'],
                    'meins': material['meins'],
                    'ersda': material['ersda'],
                    'zzextwg': material['zzextwg'],
                    'mtpos': material['mtpos'],
                    'prodh': material['prodh'],
                    'vtexT_TR': material['vtexT_TR'],
                    'vtexT_EN': material['vtexT_EN'],
                    'ntgew': material['ntgew'],
                    'zZ_BDTINGTNM': material['zZ_BDTINGTNM'],
                    'zbdT_MLZTANIM': material['zbdT_MLZTANIM'],
                    'zzbolG15': material['zzbolG15'],
                    'e_MODEL_T': material['e_MODEL_T'],
                    'e_UNITE_T': material['e_UNITE_T'],
                    'brgew': material['brgew'],
                    'zzbdT_KAPADEDI': material['zzbdT_KAPADEDI'],
                    'volum': material['volum'],
                    'vmstd': material['vmstd'],
                    'vmsta': material['vmsta'],
                    'zbdT_KARTELA': material['zbdT_KARTELA'],
                    'zbdT_URETICI': material['zbdT_URETICI'],
                    'mvgR1': material['mvgR1'],
                    'zzbolG14': material['zzbolG14'],
                    'zzbolG13': material['zzbolG13'],
                    'zzbolG12': material['zzbolG12'],
                    'zzbolG11': material['zzbolG11'],
                    'zzbolG10': material['zzbolG10'],
                    'zzbolG09': material['zzbolG09'],
                    'zzbolG08': material['zzbolG08'],
                    'zzbolG02': material['zzbolG02'],
                    'zzbolG03': material['zzbolG03'],
                    'zzbolG04': material['zzbolG04'],
                    'zzbolG05': material['zzbolG05'],
                    'zzbolG06': material['zzbolG06'],
                    'maktx': material['maktx'],
                    'e_EXTWG_E': material['e_EXTWG_E'],
                    'e_FLART_E': material['e_FLART_E'],
                    'e_UNITE_E': material['e_UNITE_E'],
                    'e_MODEL_E': material['e_MODEL_E'],
                    'e_EXTWG_T': material['e_EXTWG_T'],
                    'e_FLART_T': material['e_FLART_T'],
                    'company_id': company_id

                })
                odooProduct.write({
                    'bellona_material_ids': [[4, odooMaterials.id]]
                })
            else:
                odooMaterials.write({
                    'matnr': material['matnr'],
                    'meins': material['meins'],
                    'ersda': material['ersda'],
                    'zzextwg': material['zzextwg'],
                    'mtpos': material['mtpos'],
                    'prodh': material['prodh'],
                    'vtexT_TR': material['vtexT_TR'],
                    'vtexT_EN': material['vtexT_EN'],
                    'ntgew': material['ntgew'],
                    'zZ_BDTINGTNM': material['zZ_BDTINGTNM'],
                    'zbdT_MLZTANIM': material['zbdT_MLZTANIM'],
                    'zzbolG15': material['zzbolG15'],
                    'e_MODEL_T': material['e_MODEL_T'],
                    'e_UNITE_T': material['e_UNITE_T'],
                    'brgew': material['brgew'],
                    'zzbdT_KAPADEDI': material['zzbdT_KAPADEDI'],
                    'volum': material['volum'],
                    'vmstd': material['vmstd'],
                    'vmsta': material['vmsta'],
                    'zbdT_KARTELA': material['zbdT_KARTELA'],
                    'zbdT_URETICI': material['zbdT_URETICI'],
                    'mvgR1': material['mvgR1'],
                    'zzbolG14': material['zzbolG14'],
                    'zzbolG13': material['zzbolG13'],
                    'zzbolG12': material['zzbolG12'],
                    'zzbolG11': material['zzbolG11'],
                    'zzbolG10': material['zzbolG10'],
                    'zzbolG09': material['zzbolG09'],
                    'zzbolG08': material['zzbolG08'],
                    'zzbolG02': material['zzbolG02'],
                    'zzbolG03': material['zzbolG03'],
                    'zzbolG04': material['zzbolG04'],
                    'zzbolG05': material['zzbolG05'],
                    'zzbolG06': material['zzbolG06'],
                    'maktx': material['maktx'],
                    'e_EXTWG_E': material['e_EXTWG_E'],
                    'e_FLART_E': material['e_FLART_E'],
                    'e_UNITE_E': material['e_UNITE_E'],
                    'e_MODEL_E': material['e_MODEL_E'],
                    'e_EXTWG_T': material['e_EXTWG_T'],
                    'e_FLART_T': material['e_FLART_T'],

                })
                odooProduct.write({
                    'bellona_material_ids': [[4, odooMaterials.id]]
                })

    def importPriceScheduler(self):
        bellona_company = self.env['bellona.credentials'].search([])
        for company in bellona_company:

            token = company.token
            company_id=company.company_id.id
            url = self.getBaseURL() + "api/Material/SearchPrice"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token,
            }
            odooProducts = self.env['product.template'].search([('default_code', '!=', False), ('company_id', '=', company_id)])
            for odooProduct in odooProducts:
                payload = json.dumps(odooProduct.default_code)
                response = requests.request("POST", url, headers=headers, data=payload)
                if response.status_code == 200:
                    product = json.loads(response.content)
                    self.updatePriceScheduler(odooProduct, product,company_id)
                else:
                    log_notes=self.env["bellona.log.notes"].sudo().create({"error":"Price"+company.company_id.name+ ": "+ str(response.text)})
        self.env.cr.commit()

    def updatePriceScheduler(self, odooProduct, product,company_id):
        odooProduct.write({
            'standard_price': product[0]['biriM_FIYAT']
        })
        shipment_obj = self.env['bellona.shipments'].search([('productcode', '=', odooProduct.default_code), ('company_id', '=', company_id)],limit=1)
        material_obj = self.env['bellona.material'].search(
            [('matnr', '=', odooProduct.default_code), ('company_id', '=',company_id)], limit=1)
        if shipment_obj:
            for shipment in shipment_obj:
                shipment.maktx = product[0]['maktx']
                shipment.datab = product[0]['datab']
                shipment.datbi = product[0]['datbi']
                shipment.konwa = product[0]['konwa']
                shipment.kbetr = product[0]['kbetr']
                shipment.kpein = product[0]['kpein']
                shipment.biriM_FIYAT = product[0]['biriM_FIYAT']
        if material_obj:
            material_obj.maktx = product[0]['maktx']
            material_obj.datab = product[0]['datab']
            material_obj.datbi = product[0]['datbi']
            material_obj.konwa = product[0]['konwa']
            material_obj.kbetr = product[0]['kbetr']
            material_obj.kpein = product[0]['kpein']
            material_obj.biriM_FIYAT = product[0]['biriM_FIYAT']
