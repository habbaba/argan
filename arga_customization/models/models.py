# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from datetime import timedelta

class ProjectTaskInh(models.Model):
    _inherit = 'project.task'

    delivery_date = fields.Datetime(string='Delivery Date', copy=False)

    def write(self, vals):
        res = super(ProjectTaskInh, self).write(vals)
        if vals.get('delivery_date'):
            if self.sale_line_id.order_id.delivery_date != self.delivery_date:
                self.sale_line_id.order_id.delivery_date = self.delivery_date


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
    total_qty = fields.Float('Total Lines', compute='_compute_total_qty')
    istikabl_qty = fields.Float('Istikabal', compute='_compute_total_qty')
    bellona_qty = fields.Float('Bellona', compute='_compute_total_qty')
    po_qty = fields.Float('PO', compute='_compute_total_qty')
    do_qty = fields.Float('DO', compute='_compute_total_qty')
    received_qty = fields.Float('Received', compute='_compute_total_qty')
    remaining_qty = fields.Float('Not Available Qty')
    receipt_status = fields.Selection(selection=[
        ('draft', 'Draft'), ('waiting', 'Waiting for another Operations'),
        ('confirmed', 'Waiting'), ('assigned', 'Ready'),
        ('done', 'Done'),  ('cancel', 'Cancelled'),('', '    ')
    ], string='Receipt Status', compute='_compute_total_qty', readonly=True, copy=False)
    do_status = fields.Selection(selection=[
        ('draft', 'Draft'), ('waiting', 'Waiting for another Operations'),
        ('confirmed', 'Waiting'), ('assigned', 'Ready'),
        ('done', 'Done'), ('cancel', 'Cancelled')
    ], string='DO Status', compute='_compute_total_qty', readonly=True, copy=False)
    po_state = fields.Selection([
        ('draft', 'Draft RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),('', '    ')
    ], 'PO Status', compute='_compute_total_qty', readonly=True)


    @api.depends('invoice_ids', 'invoice_ids.amount_total', 'invoice_ids.amount_residual','invoice_ids.amount_residual_signed')
    def compute_invoices_amount(self):
        for rec in self:
            amount = sum(rec.invoice_ids.mapped('amount_total'))
            due = sum(rec.invoice_ids.mapped('amount_residual'))
            rec.total_invoice_amount = amount
            rec.total_invoice_paid = amount - due
            rec.total_open_amount = rec.amount_total-rec.total_invoice_paid

    def _compute_total_qty(self):
        for rec in self:
            purchase_order=self.env['purchase.order'].search([("origin","=",rec.name)])
            receipt = self.env['purchase.order'].search([("origin", "=", rec.name)],limit=1)
            po_qty=0
            istikabl_qty=0
            bellona_qty=0
            received_qty=0
            for po in purchase_order:
                po_qty=po_qty+po.total_lines
                istikabl_qty=istikabl_qty+po.total_istikbal_lines
                bellona_qty= bellona_qty+po.total_bellona_lines
                received_qty=received_qty+po.total_received
            rec.po_qty=po_qty
            rec.istikabl_qty=istikabl_qty
            rec.bellona_qty=bellona_qty
            rec.received_qty=received_qty
            rec.total_qty=len(rec.order_line.filtered(lambda i: i.product_id.type == 'product').mapped('id'))
            rec.do_qty=len(self.env['stock.move.line'].search([("origin","=",rec.name),("state","=",'done')]))


            if receipt:
                rec.receipt_status=receipt.receipt_status
                rec.po_state=receipt.state
            else:
                rec.receipt_status = ''
                rec.po_state = ''

            rec.do_status = 'draft'
            if rec.picking_ids:
                if all(line.state == 'waiting' for line in rec.picking_ids):
                    rec.do_status = 'waiting'
                if all(line.state == 'confirmed' for line in rec.picking_ids):
                    rec.do_status = 'confirmed'
                if all(line.state == 'assigned' for line in rec.picking_ids):
                    rec.do_status = 'assigned'
                if all(line.state == 'done' for line in rec.picking_ids):
                    rec.do_status = 'done'
                if all(line.state == 'cancel' for line in rec.picking_ids):
                    rec.do_status = 'cancel'


    def write(self, vals):
        res = super(SaleOrderInh, self).write(vals)
        if vals.get('delivery_date'):
            project_task = self.env['project.task'].search([("sale_line_id.order_id", '=', self.id)], limit=1)
            project_task.delivery_date=self.delivery_date
            project_task.planned_date_begin=self.delivery_date
            project_task.date_deadline=self.delivery_date
            for k in self.picking_ids:
                if k.state not in ['done','cancel']:
                    k.delivery_date=self.delivery_date
        return res


class SaleOrderLineInh(models.Model):
    _inherit = 'sale.order.line'

    number = fields.Integer(string="Sr#",compute='_compute_get_number',default=1)
    available = fields.Float('Available Qty', related="product_id.qty_available")
    remaining_qty = fields.Float('Not Available')
    qty_in = fields.Float()
    qty_out = fields.Float()
    free_qty = fields.Float()

    # @api.depends('product_id')
    # def compute_in(self):
    #     for rec in self:
    #         if rec.product_uom_qty > rec.available:
    #             rec.remaining_qty = rec.product_uom_qty - rec.available
    #         else:
    #             rec.remaining_qty = 0
    #         qty_in = rec.product_id.incoming_qty
    #         qty_out = 0
    #         rec.qty_in = qty_in
    #         rec.qty_out = qty_out
    #
    #         rec.free_qty=(rec.available+rec.qty_in)-rec.qty_out


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
    delivery_date = fields.Datetime(string='Delivery Date', copy=False)


    def _compute_total_amt(self):
        for i in self:
            sale_order=self.env['sale.order'].search([("name",'=',i.origin)],limit=1)
            i.invoice_total=sale_order.amount_total
            i.remaining_amt=sale_order.total_open_amount

    def write(self, vals):
        res = super(StockPickingInh, self).write(vals)
        if vals.get('delivery_date'):
            sale_order = self.env['sale.order'].search([("name", '=', self.origin)], limit=1)
            if sale_order and sale_order.delivery_date!=self.delivery_date:
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
    receipt_status = fields.Selection(selection=[
        ('draft', 'Draft'), ('waiting', 'Waiting for another Operations'),
        ('confirmed', 'Waiting'), ('assigned', 'Ready'),
        ('done', 'Done'),  ('cancel', 'Cancelled')
    ], string='Receipt Status', compute='_compute_sale_order', readonly=True, copy=False)

    total_lines = fields.Integer(compute='_compute_lines')
    total_istikbal_lines = fields.Integer(string="Istikbal Lines",compute='_compute_lines')
    total_bellona_lines = fields.Integer(string="Bellona Lines",compute='_compute_lines')
    total_received = fields.Integer(string="Received",compute='_compute_lines')

    @api.depends('order_line','istikbal_shp_details','bellona_shipments','picking_ids')
    def _compute_lines(self):
        for rec in self:
            moves = len(self.env['stock.move.line'].search([("move_id.picking_id.purchase_id", '=', rec.id),("state", '=', 'done')]))
            rec.total_lines = len(rec.order_line.mapped('id'))
            rec.total_istikbal_lines = len(rec.istikbal_shp_details.mapped('id'))
            rec.total_bellona_lines = len(rec.bellona_shipments.mapped('id'))
            rec.total_received = moves if moves else 0


    def _compute_sale_order(self):
        for rec in self:
            rec.receipt_status = 'draft'
            if rec.picking_ids:
                if all(line.state == 'waiting' for line in rec.picking_ids):
                    rec.receipt_status = 'waiting'
                if all(line.state == 'confirmed' for line in rec.picking_ids):
                    rec.receipt_status = 'confirmed'
                if all(line.state == 'assigned' for line in rec.picking_ids):
                    rec.receipt_status = 'assigned'
                if all(line.state == 'done' for line in rec.picking_ids):
                    rec.receipt_status = 'done'
                if all(line.state == 'cancel' for line in rec.picking_ids):
                    rec.receipt_status = 'cancel'
            sale_order=self.env['sale.order'].search([("name",'=',rec.origin)],limit=1).id
            rec.sale_order=sale_order
            

class PurchaseOrderLineInh(models.Model):
    _inherit = 'purchase.order.line'

    number = fields.Integer(compute='_compute_get_number', store=True)

    @api.depends('sequence', 'order_id')
    def _compute_get_number(self):
        for order in self.mapped('order_id'):
            number = 1
            for line in order.order_line:
                line.number = number
                number += 1           




