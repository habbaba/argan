# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    total_qty = fields.Float('Total Storable Qty', compute='_compute_total_qty')
    remaining_qty = fields.Float('Not Available', compute='_compute_total_qty')

    @api.depends("order_line.product_id","order_line.product_uom_qty")
    def _compute_total_qty(self):
        total = 0
        remain_total = 0
        self.remaining_qty = 0
        for i in self.order_line:

            if i.product_id.detailed_type=="product":
                remain_total=remain_total+i.remaining_qty
                total=total+i.product_uom_qty
            self.total_qty=total
            self.remaining_qty = remain_total


class SaleOrderLineInh(models.Model):
    _inherit = 'sale.order.line'

    available = fields.Float('Available Qty', compute='_compute_total_qty')
    remaining_qty = fields.Float('Not Available', compute='_compute_total_qty')

    @api.depends("product_id")
    def _compute_total_qty(self):
        for i in self:
            quant_ids = self.env['stock.quant'].sudo().search([('product_id', '=', i.product_id.id), ('location_id.usage', '=', 'internal')]).mapped("quantity")
            total=sum(quant_ids)
            i.available=total
            if i.product_uom_qty>total:
                i.remaining_qty=i.product_uom_qty-total
            else:
                i.remaining_qty=0





class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    invoice_total = fields.Float('Invoice Total', compute='_compute_total_amt')
    remaining_amt = fields.Float('Amount due', compute='_compute_total_amt')


    def _compute_total_amt(self):
        for i in self:
            sale_order=self.env['sale.order'].search([("name",'=',i.origin)],limit=1)
            invoices=sum(self.env['account.move'].search([("invoice_origin",'=',i.origin)]).mapped("amount_residual"))
            i.invoice_total= sale_order.amount_total
            if invoices>0:
                i.remaining_amt=  invoices
            else:
                i.remaining_amt = sale_order.amount_total
