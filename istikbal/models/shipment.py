# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import json
from datetime import datetime


class Shipments(models.Model):
    _name = 'istikbal.shipments.header'

    containerNumber = fields.Char('Container Number')
    truckPlate = fields.Char('Truck Plate')
    truckPlate2 = fields.Char('Truck Plate 2')
    shipmentDate = fields.Datetime('Shipment Date')
    invoiceNumber = fields.Char('Invoice Number')
    shipmentNumber = fields.Char('Shipment Number')
    name = fields.Char('Shipment Number')
    volume = fields.Float('Volume')
    detail_ids = fields.One2many('istikbal.shipments.details', 'shipment_id', string='Shipment Details')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)


class ShipmentDetails(models.Model):
    _name = 'istikbal.shipments.details'

    shipment_id = fields.Many2one('istikbal.shipments.header')
    packageNum = fields.Char('Package Number')
    shipmentNumber = fields.Char('Shipment Number')
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
    zzbdtAmount = fields.Char('Amount')


