from odoo import models, fields, api



class ArgaTranport(models.Model):
    _name="arga.transport"
    
    name= fields.Char(string = 'Tour Nr')
    date_load= fields.Date(string = 'Date of Load')
    from_country= fields.Many2one('res.country' ,string = 'From')
    to_country= fields.Many2one('res.country' ,string = 'To')
    customer_id= fields.Many2one('res.partner' ,string = 'Customer')
    inc_nr= fields.Char(string = 'Inc nr')
    cost_without_vat= fields.Float(string = 'Cost without vat')
    vat19 = fields.Float(string = 'Vat 19%')
    cost_total = fields.Float(string = 'Cost Total', compute ='clacTotalCost' ,store=True)
    cost_paid = fields.Float(string = 'Paid',)
    open_cost= fields.Float(string = 'Open', compute='calcOpenCost' ,store=True)
    vendor_id= fields.Many2one('res.partner' ,string = 'Vendor( CARRIER )')
    incoming_inc= fields.Char(string = 'Incoming inc')
    vend_cost= fields.Float(string = 'Cost')
    vat_zero = fields.Float(string = 'Vat 0%')
    vend_paid= fields.Float(string = 'Paid 2')
    vend_open= fields.Float(string = 'Open 2' ,compute='calcOpenSecCost',store=True)
    truck_nr =fields.Char(string = 'Truck nr')
    plate_nr =fields.Char(string = 'Plate nr')
    daily_report =fields.Many2one('res.country' ,string ='Daily Report')
    send_status = fields.Text(string="Send status")
    doc_changing = fields.Char(string = 'Doc changing')
    europe_office =fields.Many2one('res.country' ,string ='Custom office in europe')
    europe_customs = fields.Date(string = 'customs in europe')
    tour_status = fields.Char(string = 'Tour status')
    spalte_four =fields.Char(string = 'Spalte 4')
    spalte_five = fields.Char(string = 'Spalte 5')
    spalte_six =fields.Char(string = 'Spalte 6')
    
    
    
    @api.depends('cost_without_vat','vat19')
    def clacTotalCost(self):
        for rec in self:
            rec.cost_total = rec.cost_without_vat +  rec.vat19
    
    
    @api.depends('cost_without_vat','vat19' ,'cost_paid')
    def calcOpenCost(self):
        for rec in self:
            rec.open_cost = (rec.cost_without_vat +  rec.vat19)  - rec.cost_paid
    
    @api.depends('vend_cost','vat_zero' ,'vend_paid')
    def calcOpenSecCost(self):
        for rec in self:
            rec.vend_open = (rec.vend_cost +  rec.vat_zero)  - rec.vend_paid
    
         
