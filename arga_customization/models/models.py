# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime



class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    delivery_date = fields.Date(string='Delivery Date', default=fields.Date.context_today, copy=False)
    total_invoice_paid = fields.Float(compute='compute_invoices_amount')
    total_invoice_amount = fields.Float(compute='compute_invoices_amount')
    total_open_amount = fields.Float(compute='compute_invoices_amount')
    total_qty = fields.Float('Total Storable Qty', compute='_compute_total_qty')
    remaining_qty = fields.Float('Not Available Qty', compute='_compute_total_qty')

    @api.depends('invoice_ids', 'invoice_ids.amount_total', 'invoice_ids.amount_residual',
                 'invoice_ids.amount_residual_signed')
    def compute_invoices_amount(self):
        for rec in self:
            amount = sum(rec.invoice_ids.mapped('amount_total'))
            due = sum(rec.invoice_ids.mapped('amount_residual'))
            rec.total_invoice_amount = amount
            rec.total_invoice_paid = amount - due
            rec.total_open_amount = due

    def _compute_total_qty(self):
            total = 0
            remain_total = 0
            self.remaining_qty=0
            self.total_qty
            for i in self.order_line:
                if i.product_id.detailed_type=="product":
                    remain_total=remain_total+i.remaining_qty
                    total=total+i.product_uom_qty
                self.total_qty=total
                self.remaining_qty = remain_total

    # def _prepare_confirmation_values(self):
    #     return {
    #         'state': 'sale',
    #     }



class SaleOrderLineInh(models.Model):
    _inherit = 'sale.order.line'

    number = fields.Integer(compute='_compute_get_number',default=1)
    available = fields.Float('Available Qty', compute='_compute_total_qty')
    remaining_qty = fields.Float('Not Available', compute='_compute_total_qty')
    qty_in = fields.Float(compute='compute_in')
    qty_out = fields.Float(compute='compute_in')
    free_qty = fields.Float(compute='compute_in')

    @api.depends('product_id')
    def compute_in(self):
        for rec in self:
            qty_in = sum(self.env['stock.move'].search(
                [('picking_type_id.code', '=', 'incoming'), ('product_id', '=', rec.product_id.id),
                 ('picking_id.state', '=', 'assigned')]).mapped('product_uom_qty'))
            qty_out = sum(self.env['stock.move'].search(
                [('picking_type_id.code', '=', 'outgoing'), ('product_id', '=', rec.product_id.id),
                 ('picking_id.state', '=', 'assigned')]).mapped('product_uom_qty'))
            rec.qty_in = qty_in
            rec.qty_out = qty_out

            rec.free_qty=(rec.available+rec.qty_in)-rec.qty_out

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

    @api.depends('order_id')
    def _compute_get_number(self):
        for order in self.mapped('order_id'):
            number = 1
            for line in order.order_line:
                if line.product_id:
                    line.number = number
                    number += 1
                else:
                    line.number = number



class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    invoice_total = fields.Float('Order Total', compute='_compute_total_amt')
    remaining_amt = fields.Float('Open Amount', compute='_compute_total_amt')
    delivery_date = fields.Date(string='Delivery Date', default=fields.Date.context_today, copy=False)


    def _compute_total_amt(self):
        for i in self:
            sale_order=self.env['sale.order'].search([("name",'=',i.origin)],limit=1)
            i.invoice_total=sale_order.amount_total
            i.remaining_amt=sale_order.total_open_amount
            i.delivery_date=sale_order.delivery_date
