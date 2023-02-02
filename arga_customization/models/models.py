# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from datetime import timedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _name = _inherit

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('customer.number')
        return super(ResPartner, self).create(vals)


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    delivery_date = fields.Datetime(string='Delivery Date', copy=False)
    total_invoice_paid = fields.Float(compute='compute_invoices_amount')
    total_invoice_amount = fields.Float(compute='compute_invoices_amount')
    total_open_amount = fields.Float(compute='compute_invoices_amount')
    total_qty = fields.Float('Total Storable Qty', compute='_compute_total_qty')
    remaining_qty = fields.Float('Not Available Qty', compute='_compute_total_qty')

    delivery_tags = fields.Selection([
        ('ANGEBOT', 'ANGEBOT'),
        ('BESTELLT', 'BESTELLT'), ('BESTÄTIGT', 'BESTÄTIGT'),('TERMINIERT', 'TERMINIERT'),('PRODUKTION', 'PRODUKTION'),('truck', 'On Truck'),
        ('TEIL_BESTELLT', 'TEIL BESTELLT'),
        ('AUFTRAG', 'AUFTRAG'),
        ('LIEFERBEREIT', 'LIEFERBEREIT'),
        ('9_GG', '9_GG'),
        ('TEIL_lIEFERUNG', 'TEIL lIEFERUNG'),
    ], string='Delivery Tags', compute='compute_tags',inverse='_set_delivery_tags')

    def compute_tags(self):
        for rec in self:
            purchase_order_ids = self._get_purchase_orders()
            select = ''
            if purchase_order_ids.state == 'draft':
                select = 'ANGEBOT'
            if purchase_order_ids.state == 'purchase':
                select = 'AUFTRAG'
            if purchase_order_ids.order_line.mapped('product_id').ids == rec.order_line.filtered(lambda i:i.product_id.route_ids).mapped('product_id').ids:
                select = 'BESTELLT'
            if purchase_order_ids.order_line.mapped('product_id').ids == rec.order_line.filtered(lambda i:i.product_id.route_ids).mapped('product_id').ids and purchase_order_ids.state == 'purchase':
                select = 'BESTÄTIGT'
            if purchase_order_ids.order_line.mapped('product_id').ids != rec.order_line.filtered(lambda i:i.product_id.route_ids).mapped('product_id').ids:
                select = 'TEIL_BESTELLT'
            if not rec.delivery_date:
                select = 'LIEFERBEREIT'
            if rec.delivery_date:
                select = 'TERMINIERT'
            if rec.state == 'sale' and all(line.state == 'done' for line in rec.picking_ids):
                select = '9_GG'
            if rec.state == 'sale' and any(line.state != 'done' for line in rec.picking_ids):
                select = 'TEIL_lIEFERUNG'

            if rec.istikbal_shipments or rec.bellona_shipments:
                if not rec.istikbal_shp_details:
                    select = 'PRODUKTION'
            if rec.istikbal_shipments and rec.istikbal_shp_details:
                    select = 'truck'

            rec.delivery_tags = select

    def _set_delivery_tags(self):

        return True

    @api.depends('invoice_ids', 'invoice_ids.amount_total', 'invoice_ids.amount_residual',
                 'invoice_ids.amount_residual_signed')
    def compute_invoices_amount(self):
        for rec in self:
            amount = sum(rec.invoice_ids.mapped('amount_total'))
            due = sum(rec.invoice_ids.mapped('amount_residual'))
            rec.total_invoice_amount = amount
            rec.total_invoice_paid = amount - due
            rec.total_open_amount = rec.amount_total-rec.total_invoice_paid

    def _compute_total_qty(self):
        for k in self:
            total = 0
            remain_total = 0
            k.total_qty=total
            k.remaining_qty = remain_total
            for i in k.order_line:
                if i.product_id.detailed_type=="product":
                    remain_total=remain_total+i.remaining_qty
                    total=total+i.product_uom_qty
                k.total_qty=total
                k.remaining_qty = remain_total

    def write(self, vals):
        res = super(SaleOrderInh, self).write(vals)
        print(vals,self.delivery_date)
        if vals.get('delivery_date'):
            for k in self.picking_ids:
                k.delivery_date=self.delivery_date
        return res


class SaleOrderLineInh(models.Model):
    _inherit = 'sale.order.line'

    number = fields.Integer(string="Sr#",compute='_compute_get_number',default=1)
    available = fields.Float('Available Qty', related="product_id.qty_available")
    remaining_qty = fields.Float('Not Available', compute='compute_in')
    qty_in = fields.Float(compute='compute_in')
    qty_out = fields.Float(compute='compute_in')
    free_qty = fields.Float(compute='compute_in')

    @api.depends('product_id')
    def compute_in(self):
        for rec in self:
            if rec.product_uom_qty > rec.available:
                rec.remaining_qty = rec.product_uom_qty - rec.available
            else:
                rec.remaining_qty = 0
            qty_in = rec.product_id.incoming_qty
            qty_out = 0
            rec.qty_in = qty_in
            rec.qty_out = qty_out

            rec.free_qty=(rec.available+rec.qty_in)-rec.qty_out


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

    def write(self, vals):
        res = super(StockPickingInh, self).write(vals)
        if vals.get('delivery_date'):
            sale_order = self.env['sale.order'].search([("name", '=', self.origin)], limit=1)
            if sale_order and  sale_order.delivery_date!=self.delivery_date:
                sale_order.delivery_date = self.delivery_date
#                 obj = self.env['calendar.event'].search([("picking_id", '=', self.id)])
#                 if obj:
#                     obj.sudo().write({
#                         'name': self.name,
#                         'start': self.delivery_date,
#                         'duration': 1,
#                         'privacy': 'confidential',
#                         'stop':self.delivery_date + timedelta(hours=1),
#                         'description': self.note,
#                     })
        return res


#     def unlink(self):
#         res = super(StockPickingInh, self).unlink()
#         for i in self:
#             obj = self.env['calendar.event'].search([("picking_id", '=', i.id)]).unlink()
#         return res

#     @api.model_create_multi
#     def create(self, vals_list):
#         res_ids = super(StockPickingInh, self).create(vals_list)
#         res_ids._create_calander_envent()
#         return res_ids



#     def _create_calander_envent(self):

#         sale_order=self.env['sale.order'].search([("name",'=',self.origin)],limit=1)
#         print(sale_order.user_id.partner_id.id)
#         obj = self.env['calendar.event'].search([("picking_id", '=', self.id)])
#         if not obj:
#             obj = self.env['calendar.event'].create({
#                 'name': self.name,
#                 'start': self.delivery_date,
#                 'duration': 1,
#                 'partner_ids': [(6, 0, sale_order.user_id.partner_id.ids)],
#                 'privacy': 'confidential',
#                 'stop': self.delivery_date + timedelta(hours=1),
#                 'description': self.note,
#                 'picking_id': self.id,
#                 'user_id': sale_order.user_id.id,
#                 'allday': False
#             })



class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    picking_id = fields.Many2one('stock.picking', "Picking")
    
    

class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'


    sale_order = fields.Many2one('sale.order', compute='_compute_sale_order')


    def _compute_sale_order(self):
        for rec in self:
            sale_order=self.env['sale.order'].search([("name",'=',rec.origin)],limit=1).id
            rec.sale_order=sale_order
           




