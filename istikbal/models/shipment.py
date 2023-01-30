# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import json
from datetime import datetime
import qrcode
import base64
from io import BytesIO
from odoo import models, fields, api
from odoo.http import request
from odoo import exceptions, _



class IncomingShipments(models.Model):
    _name = 'istikbal.incoming.shipments'
    _description = "Istikbal incoming shipments"
    _rec_name = 'producCode'
    _order = "producCode"

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    producCode = fields.Char('Product Code')
    packageEnum = fields.Char('packageNum')
    bdtCode = fields.Char('bdtCode')
    productRef = fields.Char('productRef')
    maktx = fields.Char('maktx')
    vrkme = fields.Char('vrkme')
    lgort = fields.Char('lgort')
    volum = fields.Char('volum')
    audat = fields.Char('audat')
    stawn = fields.Char('stawn')
    quatity = fields.Char('quatity')
    customerRef = fields.Char('customerRef')
    customerBarCode = fields.Char('customerBarCode')
    text = fields.Char('text')
    quantity = fields.Char('Quantity')


class Shipments(models.Model):
    _name = 'istikbal.shipments.header'
    _description = "Istikbal shipment Headers"
    _rec_name = 'shipmentNumber'
    _order = "shipmentNumber"

    disPactDate = fields.Char('disPactDate')
    containerNumber = fields.Char('Container Number')
    truckPlate = fields.Char('Truck Plate')
    truckPlate2 = fields.Char('Truck Plate 2')
    shipmentDate = fields.Char('Shipment Date')
    invoiceNumber = fields.Char('Invoice Number')
    shipmentNumber = fields.Char('Shipment Number')
    name = fields.Char('Shipment Number')
    volum = fields.Float('volum')
    voleh = fields.Float('voleh')
    detail_ids = fields.One2many('istikbal.shipments.details', 'shipment_id', string='Shipment Details')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    is_combined = fields.Boolean(copy=False)

    def get_combine_shipments(self):
        shipments = self.env['istikbal.shipments.header'].search([('is_combined', '=', False)])
        # for t in shipments:
        #     t.is_combined = False
        for rec in shipments:
            if not rec.is_combined:
                already_exist = self.env['istikbal.combine.shipments'].search([('disPactDate', '=', rec.disPactDate), ('truckPlate', '=', rec.truckPlate)])
                if already_exist:
                    self.update_combine(rec, already_exist)
                else:
                    self.create_combine(rec)

    def update_combine(self, rec, existing):
        duplicates = self.env['istikbal.shipments.header'].search(
            [('disPactDate', '=', rec.disPactDate), ('truckPlate', '=', rec.truckPlate),
             ('is_combined', '=', False)])
        detail_list = []
        rec.is_combined = True
        ship_no = []
        for r in duplicates:
            r.is_combined = True
            ship_no.append(r.shipmentNumber)
            for s in r.detail_ids:
                detail_list.append((0, 0, {
                    # 'shipment_id': s.shipment_id.id,
                    'pakageEnum': s.pakageEnum,
                    'shipMentNumber': s.shipMentNumber,
                    'bdtCode': s.bdtCode,
                    'productCode': s.productCode,
                    'productPackage': s.productPackage,
                    'quantity': s.quantity,
                    'orderReference': s.orderReference,
                    'bdtOrderNumber': s.bdtOrderNumber,
                    'customerItemReference': s.customerItemReference,
                    'customerItemCode': s.customerItemCode,
                    'customerOrderReference': s.customerOrderReference,
                    'productName': s.productName,
                    'productNamePack': s.productNamePack,
                    'productNameEN': s.productNameEN,
                    'volum': s.volum,
                    'vrkme': s.vrkme,
                    'inhalt': s.inhalt,
                    'mvgr3Desc': s.mvgr3Desc,
                    'brgew': s.brgew,
                    'gewei': s.gewei,
                    'zzbdtAmount': s.zzbdtAmount,
                    'voleh': s.voleh,
                    # 'brgew': s.price_unit,
                }))
        exist = existing.shipmentNumber.split(',')
        ship_no = ship_no + exist
        existing.write({
            'detail_ids': detail_list,
            'shipmentNumber': ','.join(ship_no)
        })





    def create_combine(self, rec):
        duplicates = self.env['istikbal.shipments.header'].search(
            [('disPactDate', '=', rec.disPactDate), ('truckPlate', '=', rec.truckPlate),
             ('is_combined', '=', False)])
        detail_list = []
        rec.is_combined = True
        for r in duplicates:
            r.is_combined = True
            for s in r.detail_ids:
                detail_list.append((0, 0, {
                    # 'shipment_id': s.shipment_id.id,
                    'pakageEnum': s.pakageEnum,
                    'shipMentNumber': s.shipMentNumber,
                    'bdtCode': s.bdtCode,
                    'productCode': s.productCode,
                    'productPackage': s.productPackage,
                    'quantity': s.quantity,
                    'orderReference': s.orderReference,
                    'bdtOrderNumber': s.bdtOrderNumber,
                    'customerItemReference': s.customerItemReference,
                    'customerItemCode': s.customerItemCode,
                    'customerOrderReference': s.customerOrderReference,
                    'productName': s.productName,
                    'productNamePack': s.productNamePack,
                    'productNameEN': s.productNameEN,
                    'volum': s.volum,
                    'vrkme': s.vrkme,
                    'inhalt': s.inhalt,
                    'mvgr3Desc': s.mvgr3Desc,
                    'brgew': s.brgew,
                    'gewei': s.gewei,
                    'zzbdtAmount': s.zzbdtAmount,
                    'voleh': s.voleh,
                    # 'brgew': s.price_unit,
                }))
        val = {
            'disPactDate': duplicates[0].disPactDate,
            'containerNumber': rec.containerNumber,
            'truckPlate': rec.truckPlate,
            'truckPlate2': rec.truckPlate2,
            'shipmentDate': rec.shipmentDate,
            'invoiceNumber': rec.invoiceNumber,
            'shipmentNumber': ','.join(duplicates.mapped('shipmentNumber')),
            'name': rec.name,
            'volum': rec.volum,
            'voleh': rec.voleh,
            'detail_ids': detail_list,
        }
        combine = self.env['istikbal.combine.shipments'].create(val)



class ShipmentDetails(models.Model):
    _name = 'istikbal.shipments.details'
    _description = "Istikbal Shipment Details"
    _rec_name = 'shipMentNumber'
    _order = "shipMentNumber"

    shipment_id = fields.Many2one('istikbal.shipments.header')
    pakageEnum = fields.Char('Package Number')
    shipMentNumber = fields.Char('Shipment Number')
    bdtCode = fields.Char('Code')
    productCode = fields.Char('Product Code')
    productPackage = fields.Char('Product Package')
    quantity = fields.Float('Quantity')
    orderReference = fields.Char('Order Reference')
    bdtOrderNumber = fields.Char('Order Number')
    customerItemReference = fields.Char('Customer Item Reference')
    customerItemCode = fields.Char('Customer Item Code')
    customerOrderReference = fields.Char('Customer Order Reference')
    productName = fields.Char('Product Name')
    productNamePack = fields.Char('Product Name Pack')
    productNameEN = fields.Char('Product Name Eng.')
    volum = fields.Float('Volume')
    vrkme = fields.Char('vrkme')
    inhalt = fields.Char('inhalt')
    mvgr3Desc = fields.Char('mvgr3Desc')
    brgew = fields.Char('brgew')
    gewei = fields.Char('gewei')
    zzbdtAmount = fields.Char('zzbdtAmount')
    voleh = fields.Char('voleh')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                default=lambda self: self.env.company)

    qr_image = fields.Binary("QR Code", compute='_generate_qr_code')

    purchase_id = fields.Many2one('purchase.order',compute="compute_the_purchase_id")


    def compute_the_purchase_id(self):
        for i in self:
            code=str(''.join([n for n in i.customerItemCode if n.isdigit()]))
            po = self.env['purchase.order'].search([("code", '=', code)], limit=1)
            i.purchase_id=po.id

    def _generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=4,
        )
        qr.add_data(self.productCode )
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_img = base64.b64encode(temp.getvalue())
        self.qr_image=qr_img


    def confirm_purchase_receipt(self):
        for i in self:
            code=str(''.join([n for n in i.customerItemCode if n.isdigit()]))
            po=self.env['purchase.order'].search([("code",'=',code)],limit=1)
            for k in po.picking_ids:
                if k.state not in ['cancel','done']:
                    k.button_validate()

class SalesOrderAnalysis(models.Model):
    _name = 'istikbal.sales.order.analysis'
    _description = "Istikbal Sale order Analysis"

    
    
    
    
    
    
    
    
    
    
    
    
    
    
