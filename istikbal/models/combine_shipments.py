import base64
from io import BytesIO
from odoo.exceptions import UserError, ValidationError

import qrcode

from odoo import fields, models


class IstikbalLogNotes(models.Model):
    _name = 'istikbal.combine.shipments'
    _description = "Combine Shipments"
    _rec_name = 'truckPlate'

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

    total_lines = fields.Integer(compute='compute_line')
    total_value = fields.Integer(compute='compute_line')

    def action_receive_po(self):
        try:
            purchase_order = self.detail_ids.mapped('purchase_id')
            for po in purchase_order:
                if po.state == 'purchase':
                    products_codes = self.detail_ids.filtered(lambda j: j.purchase_id.id == po.id and not j.is_received).mapped(
                        'productCode')
                    lines = po.order_line.filtered(lambda i: i.product_id.default_code in products_codes)
                    if lines:
                        for move in lines.move_ids:
                            move.quantity_done = move.product_uom_qty
                        if len(lines.move_ids) > 1:
                            action_data = lines.move_ids.picking_id.with_context(skip_backorder=False).button_validate()
                            if action_date:
                                backorder_wizard = self.env['stock.backorder.confirmation'].with_context(action_data['context'])
                                backorder_wizard.process()
                        else:
                            action_data = lines.move_ids.picking_id.with_context(skip_backorder=False).button_validate()
                        # for k in self
                        for r in self.detail_ids:
                            if r.purchase_id.id == po.id:
                                r.is_received = True
                            if r.productCode in products_codes:
                                r.picking_id = lines.move_ids.picking_id
        except Exception as e:
           raise ValidationError(_str(e))

    def compute_line(self):
        self.total_lines = len(self.detail_ids)
        self.total_value = sum(self.detail_ids.mapped('subtotal'))

    def cron_merger_of_header(self):
        self.merge_header()
        return

    def merge_header(self):
        recs = self.env['istikbal.shipments.header'].search([])
        combine_obj = self.env['istikbal.combine.shipments']
        for rec in recs:
            combine_rec = self.search([('truckPlate', '=', rec.truckPlate), ('shipmentDate', '=', rec.shipmentDate),
                                       ('company_id', '=', rec.company_id.id)])
            if combine_rec:
                rec.detail_ids.write({'combine_id': combine_rec.id})
                rec.combine_id = combine_rec
            else:
                combine_rec = combine_obj.create({'disPactDate': rec.disPactDate,
                                                  'containerNumber': rec.containerNumber,
                                                  'truckPlate': rec.truckPlate,
                                                  'truckPlate2': rec.truckPlate2,
                                                  'shipmentDate': rec.shipmentDate,
                                                  'invoiceNumber': rec.invoiceNumber,
                                                  'name': rec.name,
                                                  'volum': rec.volum,
                                                  'voleh': rec.voleh,
                                                  'company_id': rec.company_id.id,
                                                  })
                rec.detail_ids.write({'combine_id': combine_rec.id})
                rec.combine_id = combine_rec
        return

    def confirm_purchase_receipt(self):
        for i in self.detail_ids:
            po = self.env['purchase.order'].search([("name", '=', i.customerItemCode)], limit=1)
            if i.purchase_id and po:
                for k in po.picking_ids:
                    if k.state not in ['cancel', 'done']:
                        for mv in k.move_ids_without_package or k.move_lines:
                            mv.quantity_done = mv.product_uom_qty
                        k.button_validate()
                        for mv in k.move_ids_without_package or k.move_lines:
                            mv._action_done()
                            i.is_received = True
