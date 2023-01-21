from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
import json
import requests
import base64
import time
from datetime import datetime, timedelta
from odoo.exceptions import AccessError

class BeloonaPTInherit(models.Model):
    _inherit = 'product.template'

    bellona_material_ids = fields.Many2many('bellona.material', string='Bellona Materials')

    def importBellonaMaterials(self):
        try:
            token = self.env['res.config.settings'].getBellonaCredentials()
            url = self.env['res.config.settings'].getBaseURL() + "api/Material/SearchMaterial"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token,
            }
            data = {
                "matnr": self.default_code,
                 "date": "2013-01-01"
            }
            payload = json.dumps(data)
            response = requests.request("POST", url, headers=headers, data=payload)

            if response.status_code == 200:
                products = json.loads(response.content)
                print("Material response", products)
                self.createBellonaMaterials(products)
            else:
                raise UserError(_('Error %s .', response))
            self.env.cr.commit()
        except Exception as e:
            if "Connection aborted" in str(e):
                raise UserError(_('Error %s .', str(e)))

    def createBellonaMaterials(self, materials):
        for material in materials:
            odooMaterials = self.env['bellona.material'].search([('matnr', '=', material['matnr'])])
            if not odooMaterials:
                odooMaterials = self.env['bellona.material'].create({
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
                    'product_template': self.id,
                })
                self.write({
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
                    'product_template': self.id,
                })
                self.write({
                    'bellona_material_ids': [[4, odooMaterials.id]]
                })
            self.importPrice(material['matnr'])


    def importPrice(self,code):
        token = self.env['res.config.settings'].getBellonaCredentials()
        url = self.env['res.config.settings'].getBaseURL() + "api/Material/SearchPrice"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }
        odooProducts = self.env['product.template'].search([('default_code', '=',code)])
        for odooProduct in odooProducts:
            payload = json.dumps(odooProduct.default_code)
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                product = json.loads(response.content)
                self.updatePrice(odooProduct, product)
            else:
                raise UserError(_('Coach of Error %s .', response.text))
        self.env.cr.commit()

    def updatePrice(self, odooProduct, product):
        odooProduct.write({
            'standard_price': product[0]['biriM_FIYAT']
        })
        shipment_obj = self.env['bellona.shipments'].search([('productcode', '=', odooProduct.default_code)])
        material_obj = self.env['bellona.material'].search([('matnr', '=', odooProduct.default_code)],limit=1)
        if shipment_obj:
            for shipment in shipment_obj:
                shipment.maktx = product[0]['maktx']
                shipment.datab = product[0]['datab']
                shipment.datbi = product[0]['datbi']
                shipment.konwa = product[0]['konwa']
                shipment.kbetr = product[0]['kbetr']
                shipment.kpein = product[0]['kpein']
                shipment.biriM_FIYAT = product[0]['biriM_FIYAT']
        if  material_obj:
            material_obj.maktx = product[0]['maktx']
            material_obj.datab = product[0]['datab']
            material_obj.datbi = product[0]['datbi']
            material_obj.konwa = product[0]['konwa']
            material_obj.kbetr = product[0]['kbetr']
            material_obj.kpein = product[0]['kpein']
            material_obj.biriM_FIYAT = product[0]['biriM_FIYAT']


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    bellona_shipments = fields.Many2many('bellona.shipments', string='Bellona Shipments')

class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    bellona_shipments = fields.Many2many('bellona.shipments', string='Bellona Shipments')
    code = fields.Char(string='Code',compute="compute_the_code")



    def compute_the_code(self):
        for k in self:
            k.code=str(''.join([n for n in k.name if n.isdigit()]))