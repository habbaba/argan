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
    combine_id = fields.Many2one('istikbal.combine.shipments')


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
    purchase_id = fields.Many2one('purchase.order', compute="_generate_qr_code")
    combine_id = fields.Many2one('istikbal.combine.shipments')
    is_received = fields.Boolean('Received')
    # is_processed = fields.Boolean('Received')
    price = fields.Float()
    picking_id = fields.Many2one('stock.picking')
    subtotal = fields.Float(compute='compute_subtotal')

    @api.depends('price', 'quantity')
    def compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.price * rec.quantity

    def action_receive_po(self):
        if self.purchase_id.state == 'purchase':
            lines = self.purchase_id.order_line.filtered(lambda i: i.product_id.default_code == self.productCode)
            if lines:
                if not self.picking_id:
                        self.picking_id = lines.move_ids.filtered(
                            lambda h: h.product_id.default_code == self.productCode).picking_id.id
                        if self.picking_id.state == 'done':
                            self.is_received = True
                for move in lines.move_ids:
                    if move.state not in ['done', 'cancel']:
                        move.quantity_done = move.product_uom_qty
                # if self.purchase_id.name == 'BNR*85 * 00013':
                #     print('hhh')
                if len(lines.move_ids) > 1:
                    action_data = lines.move_ids.filtered(
                        lambda h: h.state not in ['done', 'cancel']).picking_id.with_context(
                        skip_backorder=False).button_validate()
                    # print(action_data)
                    backorder_wizard = self.env['stock.backorder.confirmation'].with_context(action_data['context'])
                    backorder_wizard.process()
                        # if r.purchase_id.id == po.id:
                        #     r.is_received = True
                        # if r.productCode in products_codes:
                    if not self.picking_id:
                        self.picking_id = lines.move_ids.filtered(
                            lambda h: h.product_id.default_code == self.productCode).picking_id.id
                        if self.picking_id.state == 'done':
                            self.is_received = True
                    # self.is_received = True
                else:
                    action_data = lines.move_ids.filtered(
                        lambda h: h.state not in ['done', 'cancel']).picking_id.with_context(
                        skip_backorder=False).button_validate()
                    if not self.picking_id:
                        self.picking_id = lines.move_ids.filtered(
                            lambda h: h.product_id.default_code == self.productCode).picking_id.id
                        if self.picking_id.state == 'done':
                            self.is_received = True
                    # self.is_received = True

    def _generate_qr_code(self):
        for i in self:
            po = self.env['purchase.order'].search([("name", '=', i.customerItemCode)], limit=1)
            i.purchase_id = po.id
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=20,
                border=4,
            )
            qr.add_data(i.productCode)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_img = base64.b64encode(temp.getvalue())
            i.qr_image = qr_img

    # def confirm_purchase_receipt(self):
    #     for i in self:
    #         po = self.env['purchase.order'].search([("name", '=', i.customerItemCode)],limit=1)
    #         if i.purchase_id and po:
    #             for k in po.picking_ids:
    #                 if k.state not in ['cancel','done']:
    #                     for mv in k.move_ids_without_package or k.move_lines:
    #                         mv.quantity_done = mv.product_uom_qty
    #                     k.button_validate()
    #                     for mv in k.move_ids_without_package or k.move_lines:
    #                         mv._action_done()
    #                         i.is_received=True


class SalesOrderAnalysis(models.Model):
    _name = 'istikbal.sales.order.analysis'
    _description = "Istikbal Sale order Analysis"
