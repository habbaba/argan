from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
import json
import requests
import base64
import time
from datetime import datetime, timedelta


class PTInherit(models.Model):
    _inherit = 'product.template'

    bellona_material_ids = fields.Many2many('bellona.material', string='Bellona Materials')

    def importMaterials(self):
        token = self.env['res.config.settings'].getCredentials()
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
        print("response",response)
        if response.status_code == 200:
            products = json.loads(response.content)
            # print("Material response", products)
            self.createMaterials(products)
        else:
            currentCompany = self.env.company
            bellonaCredentials = self.env['bellona.credentials'].search([('company_id', '=', currentCompany.id),
                                                                         ('active', '=', True)], limit=1)
            bellonaCredentials.connect_credentials()
            self.importMaterials()
        self.env.cr.commit()

    def createMaterials(self, materials):
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