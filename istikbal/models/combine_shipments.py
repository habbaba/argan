import base64
from io import BytesIO

import qrcode

from odoo import fields, models


class IstikbalLogNotes(models.Model):
    _name = 'istikbal.combine.shipments'
    _description = "Combine Shipments"
    _rec_name='truckPlate'

    disPactDate = fields.Char('disPactDate')
    containerNumber = fields.Char('Container Number')
    truckPlate = fields.Char('Truck Plate')
    truckPlate2 = fields.Char('Truck Plate 2')
    shipmentDate = fields.Char('Shipment Date')
    invoiceNumber = fields.Char('Invoice Number')
    name = fields.Char('Shipment Number')
    volum = fields.Float('volum')
    voleh = fields.Float('voleh')
    detail_ids = fields.One2many('istikbal.shipments.details', 'combine_id', string='Shipment Details')
    company_id = fields.Many2one('res.company', string='Company')
    shipment_ids = fields.One2many('istikbal.shipments.header', 'combine_id')

       
    def cron_merger_of_header(self):
        self.merge_header()
        return

    def merge_header(self):
        recs = self.env['istikbal.shipments.header'].search([])
        combine_obj = self.env['istikbal.combine.shipments']
        for rec in recs:
            combine_rec = self.search([('truckPlate','=', rec.truckPlate), ('shipmentDate', '=', rec.shipmentDate)])
            if combine_rec:
                rec.detail_ids.write({'combine_id':combine_rec.id})
                rec.combine_id = combine_rec
            else:
                
                combine_rec = combine_obj.create({'disPactDate' : rec.disPactDate,
                                            'containerNumber' : rec.containerNumber,
                                            'truckPlate' : rec.truckPlate,
                                            'truckPlate2' : rec.truckPlate2,
                                            'shipmentDate' : rec.shipmentDate,
                                            'invoiceNumber' : rec.invoiceNumber,
                                            'name' : rec.name,
                                            'volum' : rec.volum,
                                            'voleh' : rec.voleh,        
                                            'company_id' : rec.company_id.id,
                                            })
                rec.detail_ids.write({'combine_id':combine_rec.id})
                rec.combine_id = combine_rec
        return 


class ShipmentDetails(models.Model):
    _name = 'istikbal.combineshipments.details'
    _description = "Istikbal Combine Shipment Details"
    _rec_name = 'shipMentNumber'
    _order = "shipMentNumber"

    shipment_id = fields.Many2one('istikbal.combine.shipments')
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
    purchase_id = fields.Many2one('purchase.order', compute="compute_the_purchase_id")

    def compute_the_purchase_id(self):
        for i in self:
            po = self.env['purchase.order'].search([("name", '=', i.customerItemCode)])
            i.purchase_id = po.id

    def _generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=4,
        )
        qr.add_data(self.productCode)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_img = base64.b64encode(temp.getvalue())
        self.qr_image = qr_img

    def confirm_purchase_receipt(self):
        for i in self:
            po = self.env['purchase.order'].search([("name", '=', i.customerItemCode)], limit=1)
            for k in po.picking_ids:
                if k.state not in ['cancel', 'done']:
                    for mv in k.move_ids_without_package or k.move_lines:
                        mv.quantity_done = mv.product_uom_qty
                    k.button_validate()
                    for mv in k.move_ids_without_package or k.move_lines:
                        mv._action_done()
