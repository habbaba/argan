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
            combine_rec = self.search([('truckPlate','=', rec.truckPlate), ('shipmentDate', '=', rec.shipmentDate),('company_id', '=', rec.company_id.id)])
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
    
    
    
    
    def confirm_purchase_receipt(self):
        for i in self.detail_ids:
            po = self.env['purchase.order'].search([("name", '=', i.customerItemCode)],limit=1)
            if i.purchase_id and po:
                for k in po.picking_ids:
                    if k.state not in ['cancel','done']:
                        for mv in k.move_ids_without_package or k.move_lines:
                            mv.quantity_done = mv.product_uom_qty
                        k.button_validate()
                        for mv in k.move_ids_without_package or k.move_lines:
                            mv._action_done()
                            i.is_received=True
