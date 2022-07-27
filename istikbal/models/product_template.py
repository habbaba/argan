# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import json
from datetime import datetime
from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
import json
import requests
import base64
import time
from datetime import datetime, timedelta

class InheritPT(models.Model):
    _inherit = 'product.template'

    istikbal_product_code = fields.Char('Product Code')
    syncedIstikbal = fields.Boolean('Synced Istikbal', default=False)
    material_ids = fields.Many2many('istikbal.materials', string='Istikbal Materials')
    packageNum = fields.Char('packageNum')
    maktx = fields.Char('maktx')
    vrkme = fields.Char('vrkme')
    lgort = fields.Char('lgort')
    volum = fields.Char('volum')
    audat = fields.Char('audat')
    stawn = fields.Char('stawn')
    bdtCode = fields.Char('bdtCode')
    productRef = fields.Char('productRef')

    def get_material(self):
        username, password = self.env['res.config.settings'].search([],limit = 1).getCredentials()
        odooProducts = self.env['product.template'].search([('istikbal_product_code', '!=', False)])
        allMaterials = []
#         for odooProduct in odooProducts:
        url = "https://b2bapi.istikbal.com.tr/api/v1.0/data/getmaterial?materialNumber=" + self.istikbal_product_code
        auth = str(base64.b64encode((str(username) + ':' + str(password)).encode()), 'utf-8')
        headers = {
            'Authorization': 'Basic ' + auth,
        }

        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            materials = json.loads(response.content)
       


        self.createMaterials(materials)
        self.env.cr.commit()

    def createMaterials(self, materials):
        for material in materials:
   
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

            odooProduct =self
            odooProduct.write({
                'material_ids': [[4, odooMaterials.id]]
            })

class Materials(models.Model):
    _name = 'istikbal.materials'

    materialNumber = fields.Char('Product Code')
    bdtModelName = fields.Char('Model Name')
    bdtMaterialDesc = fields.Char('Description')
    bdtEnglishMaterailDesc = fields.Char('Description Eng.')
    netWeight = fields.Float('Net Weight')
    grossWeight = fields.Float('Gross Weight')
    numberExportContainer = fields.Integer('No. Export Container')
    volum = fields.Float('Volume')
    producerCode = fields.Char('Producer Code')
    materialGroup = fields.Char('Group')
    vmstd= fields.Char('vmstd')
    vmsta= fields.Char('vmsta')
    bdtKartela= fields.Char('bdtKartela')
    meins= fields.Char('meins')
    ersda= fields.Char('ersda')
    productClass= fields.Char('productClass')
    productClassDef= fields.Char('productClassDef')
    mtpos= fields.Char('mtpos')
    prodh= fields.Char('prodh')
    vtext= fields.Char('vtext')
    mvgr3= fields.Char('mvgr3')
    zzbolG01= fields.Char('zzbolG01')
    zzbolG02= fields.Char('zzbolG02')
    zzbolG03= fields.Char('zzbolG03')
    zzbolG04= fields.Char('zzbolG04')
    zzbolG05= fields.Char('zzbolG05')
    zzbolG06= fields.Char('zzbolG06')
    zzbolG07= fields.Char('zzbolG07')
    zzbolG08= fields.Char('zzbolG08')
    zzbolG09= fields.Char('zzbolG09')
    zzbolG10= fields.Char('zzbolG010')
    zzbolG11= fields.Char('zzbolG011')
    zzbolG12= fields.Char('zzbolG012')
    zzbolG13= fields.Char('zzbolG013')
    zzbolG14= fields.Char('zzbolG014')
    zzbolG15= fields.Char('zzbolG015')
    fabric= fields.Char('fabric')
    
    
    
    
    
    
    
  

