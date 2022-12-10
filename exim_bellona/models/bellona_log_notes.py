from odoo import _, api, fields, models

class BellonaLogNotes(models.Model):
    _name = 'bellona.log.notes'
    _description = "Bellona Logs"
    _rec_name = 'error'

    error = fields.Text('Error')
    company_id = fields.Many2one('res.company', string='Company')