# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import json
from datetime import datetime
from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import AccessError
import json
import requests
import base64
import time
from datetime import datetime, timedelta

class InheritPT(models.Model):
    _inherit = 'product.template'

    syncedIstikbal = fields.Boolean('Synced Istikbal', default=False)
    material_ids = fields.Many2many('istikbal.materials', string='Istikbal Materials')
    company_ids = fields.Many2many('res.company', string='Companies',
                                   domain=lambda self: [('id', 'in', self.env.companies.ids)])


    def get_material(self):
        try:
            username, password = self.env['res.config.settings'].search([],limit = 1).getCredentials()
            if self.default_code:
                url = "https://b2bapi.istikbal.com.tr/api/v1.0/data/getmaterial?materialNumber=" + self.default_code
                auth = str(base64.b64encode((str(username) + ':' + str(password)).encode()), 'utf-8')
                headers = {
                    'Authorization': 'Basic ' + auth,
                }

                response = requests.request("GET", url, headers=headers)
                if response.status_code == 200:
                    materials = json.loads(response.content)
                    if materials:
                        self.createMaterials(materials)
                        self.env.cr.commit()
                    else:
                        raise UserError(_("No material detail found. "+str(response.text)))
            else:
                raise UserError(_("Please add product info code."))
        except Exception as e:
           raise str(e)




    def createMaterials(self, materials):
        for material in materials:
            odooMaterials = self.env['istikbal.materials'].search([('materialNumber', '=', material['materialNumber'])])
            if odooMaterials:
                Material = self.env['istikbal.materials'].write({
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
            if odooMaterials:
                odooMaterials = self.env['istikbal.materials'].search(
                    [('materialNumber', '=', material['materialNumber'])])
                self.write({
                    'material_ids': [[4, odooMaterials.id]]
                })

class Materials(models.Model):
    _name = 'istikbal.materials'
    _description = "Istikbal Materials"
    _rec_name = 'materialNumber'
    _order = "materialNumber"

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
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
    

class IstikbalSaleOrderInh(models.Model):
    _inherit = 'sale.order'

    istikbal_shipments = fields.Many2many('istikbal.incoming.shipments', string='Istikbal Inventory',compute="compute_the_shipments")
    istikbal_shp_details = fields.Many2many('istikbal.shipments.details', string='Istikbal Shipment details',compute="compute_the_shipments")
    delivery_tags = fields.Many2many('crm.tag', 'name',string='Delivery Tags',compute="compute_the_shipments")

    def compute_the_shipments(self):
        for i in self:
            shipments = self.env['purchase.order'].search([('origin', '=', i.name)])
            i.istikbal_shipments=shipments.istikbal_shipments
            i.istikbal_shp_details=shipments.istikbal_shp_details
            tags = self.env['crm.tag'].search([('name', '=', "bestellt")])
            i.delivery_tags
            if shipments:
                tags = self.env['crm.tag'].search([('name', '=', "bestellt")])
                if not tags:
                    tags = self.env['crm.tag'].create({'name': "bestellt"})

                i.delivery_tags = tags.ids

            if i.istikbal_shipments:
                if not i.istikbal_shp_details:
                    tags= self.env['crm.tag'].search([('name', '=', "Production")])
                    if not tags:
                        tags = self.env['crm.tag'].create({'name': "Production"})

                    i.delivery_tags= tags.ids

            if i.istikbal_shipments and i.istikbal_shp_details:
                    tags = self.env['crm.tag'].search([('name', '=', "On Truck")])
                    if not tags:
                        tags = self.env['crm.tag'].create({'name': "On Truck"})

                    i.delivery_tags = tags.ids

            for k in i.picking_ids:
                if k.state=="done":
                    tags = self.env['crm.tag'].search([('name', '=', "GG")])
                    if not tags:
                        tags = self.env['crm.tag'].create({'name': "GG"})
                    i.delivery_tags = tags.ids
                if k.state=="assigned":
                    tags = self.env['crm.tag'].search([('name', '=', "LB")])
                    if not tags:
                        tags = self.env['crm.tag'].create({'name': "LB"})
                    i.delivery_tags = tags.ids



class IstikbalPurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    istikbal_shipments = fields.Many2many('istikbal.incoming.shipments', string='Istikbal Shipments',compute="compute_the_shipments")
    istikbal_shp_details = fields.Many2many('istikbal.shipments.details', string='Istikbal Shipment details',
                                            compute="compute_the_shipments")

    def compute_the_shipments(self):
        for i in self:
            inventory = self.env['istikbal.incoming.shipments'].search([('customerBarCode', '=', i.name)])
            shipment_details = self.env['istikbal.shipments.details'].search([('customerItemCode', '=', i.name)])
            i.istikbal_shipments=inventory.ids
            i.istikbal_shp_details=shipment_details.ids


    
  

