from odoo import models, fields, api



class ArgaTranport(models.Model):
    _name="arga.transport"
    
    name= fields.Char(string = 'Tour Nr', readonly=True, index=True, copy=False, default='New')
    date_load= fields.Date(string = 'Date of Load')
    from_country= fields.Many2one('res.country' ,string = 'From')
    to_country= fields.Many2one('res.country' ,string = 'To')
    customer_id= fields.Many2one('res.partner' ,string = 'Customer')
    inc_nr= fields.Char(string = 'Inc nr')
    cost_without_vat= fields.Float(string = 'Cost without vat', readonly=True,copy=False)
    vat19 = fields.Float(string = 'Vat 19%' , readonly=True, copy=False)
    cost_total = fields.Float(string = 'Cost Total', compute ='clacTotalCost' ,store=True)
    cost_paid = fields.Float(string = 'Paid', readonly=True, copy=False)
    open_cost= fields.Float(string = 'Open', compute='calcOpenCost' ,store=True)
    vendor_id= fields.Many2one('res.partner' ,string = 'Vendor( CARRIER )')
    incoming_inc= fields.Char(string = 'Incoming inc')
    vend_cost= fields.Float(string = 'Cost' ,copy=False ,readonly= True)
    vat_zero = fields.Float(string = 'Vat 0%' ,copy=False ,readonly= True)
    vend_paid= fields.Float(string = 'Paid 2' ,copy=False ,readonly= True)
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
    customer_inv = fields.Many2one('account.move' , string="Invoice")
    vendor_bill = fields.Many2one('account.move' , string="Bill")

    @api.model
    def create(self, vals):
       
        if vals.get('name', 'New') == 'New':
          
            vals['name'] = self.env['ir.sequence'].next_by_code('arga.transport') or '/'
      
        res = super(ArgaTranport, self).create(vals)
        
        return res
   
    @api.onchange('customer_inv')
    def getInvoiceData(self):
        if self.customer_inv:
            self.cost_without_vat = self.customer_inv.amount_untaxed
            self.vat19 = self.customer_inv.amount_tax
            if self.customer_inv._get_reconciled_payments():
                total_paid =  sum(self.customer_inv._get_reconciled_payments().mapped('amount')) 
                self.cost_paid  =total_paid
            
    
    
    
    
    @api.onchange('vendor_bill')
    def getInvoiceBillData(self):
        if self.vendor_bill:
            self.vend_cost = self.vendor_bill.amount_untaxed
            self.vat_zero = self.vendor_bill.amount_tax
            if self.vendor_bill._get_reconciled_payments():
                total_paid =  sum(self.vendor_bill._get_reconciled_payments().mapped('amount')) 
                self.vend_paid  =total_paid
    
    
    
    
            
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
    
         
