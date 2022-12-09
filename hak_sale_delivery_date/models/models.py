# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    def _prepare_confirmation_values(self):
        t = self.validity_date
        return {
            'state': 'sale',
            # 'date_order': fields.Datetime.now()
            'date_order':  datetime.datetime(t.year, t.month, t.day)
        }


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    scheduled_date = fields.Datetime(
        'Scheduled Date', compute='_compute_scheduled_date', inverse='_set_scheduled_date', store=True,
        index=True, default=fields.Datetime.now, tracking=True,
        help="Scheduled time for the first part of the shipment to be processed. Setting manually a value here would set it as expected date for all the stock moves.")

    date_deadline = fields.Datetime(
        "Deadline",
        help="Date Promise to the customer on the top level document (SO/PO)")
