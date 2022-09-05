from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
import requests
import json
from odoo.exceptions import ValidationError, UserError


class Credentials(models.Model):
    _name = 'bellona.credentials'

    username = fields.Char('Username')
    password = fields.Char('Password')
    token = fields.Char('Token', copy=False)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    active = fields.Boolean('Active',default=True)

    def getCredentials(self):
        currentCompany = self.env.company
        bellonaCredentials = self.env['bellona.credentials'].search([('company_id', '=', currentCompany.id),
                                                                       ('active', '=', True)])
        if len(bellonaCredentials.ids) > 1:
            raise ValidationError("Multiple Credentials are active for current company. Please select/active only one at a time.")
        elif len(bellonaCredentials.ids) == 0:
            raise ValidationError("No credential is assign to current company. Please go to Bellona->Credentials.")
        else:
            return bellonaCredentials.username, bellonaCredentials.password

    def connect_credentials(self):
        settings = self.env['res.config.settings']
        url = settings.getBaseURL() + "api/Account"
        username,  password = self.getCredentials()
        payload = json.dumps({
            "userName": username,
            "password": password
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            response = json.loads(response.text)
            self.write({
                'token': response['value']
            })