from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
import json
import requests
import base64
import time
from datetime import datetime, timedelta

INTERVAL = [
    ('minutes', 'Minutes'),
    ('hours', 'Hours'),
    ('days', 'Days'),
    ('weeks', 'Weeks'),
    ('months', 'Months')
]


class Integration(models.TransientModel):
    _inherit = 'res.config.settings'

    importInventoryButton = fields.Boolean("Import Bellona Inventory")
    importInventoryUnit = fields.Integer("Import Unit")
    importInventoryInterval = fields.Selection(INTERVAL, "Import Interval", default='months')
    importPriceButton = fields.Boolean("Import Price")
    importPriceUnit = fields.Integer("Import Unit")
    importPriceInterval = fields.Selection(INTERVAL, "Import Interval", default='months')

    def TurnOnAndOffSchedulers(self):
        if self.importInventoryButton:
            self.changeSettingsOfImportInventoryScheduler(True)

        if not self.importInventoryButton:
            self.changeSettingsOfImportInventoryScheduler(False)

        if self.importPriceButton:
            self.changeSettingsOfImportPriceScheduler(True)

        if not self.importPriceButton:
            self.changeSettingsOfImportPriceScheduler(False)

    def changeSettingsOfImportInventoryScheduler(self, state):
        scheduler = self.env['ir.cron'].search([('name', '=', 'Import Bellona Inventory')])
        if not scheduler:
            scheduler = self.env['ir.cron'].search([('name', '=', 'Import Bellona Inventory'),
                                                    ('active', '=', False)])
        scheduler.active = state
        scheduler.interval_number = self.importInventoryUnit
        scheduler.interval_type = self.importInventoryInterval

    def changeSettingsOfImportPriceScheduler(self, state):
        scheduler = self.env['ir.cron'].search([('name', '=', 'Import Price')])
        if not scheduler:
            scheduler = self.env['ir.cron'].search([('name', '=', 'Import Price'),
                                                    ('active', '=', False)])
        scheduler.active = state
        scheduler.interval_number = self.importPriceUnit
        scheduler.interval_type = self.importPriceInterval

    def set_values(self):
        res = super(Integration, self).set_values()
        self.env['ir.config_parameter'].set_param('exim_bellona.importInventoryButton', self.importInventoryButton)
        self.env['ir.config_parameter'].set_param('exim_bellona.importInventoryUnit', self.importInventoryUnit)
        self.env['ir.config_parameter'].set_param('exim_bellona.importInventoryInterval', self.importInventoryInterval)
        self.env['ir.config_parameter'].set_param('exim_bellona.importPriceButton', self.importPriceButton)
        self.env['ir.config_parameter'].set_param('exim_bellona.importPriceUnit', self.importPriceUnit)
        self.env['ir.config_parameter'].set_param('exim_bellona.importPriceInterval', self.importPriceInterval)

        self.TurnOnAndOffSchedulers()
        return res

    @api.model
    def get_values(self):
        res = super(Integration, self).get_values()
        icpsudo = self.env['ir.config_parameter'].sudo()
        importInventoryButton = icpsudo.get_param('exim_bellona.importInventoryButton')
        importInventoryUnit = icpsudo.get_param('exim_bellona.importInventoryUnit')
        importInventoryInterval = icpsudo.get_param('exim_bellona.importInventoryInterval')
        importPriceButton = icpsudo.get_param('exim_bellona.importPriceButton')
        importPriceUnit = icpsudo.get_param('exim_bellona.importPriceUnit')
        importPriceInterval = icpsudo.get_param('exim_bellona.importPriceInterval')

        res.update(
            importInventoryButton=True if importInventoryButton == 'True' else False,
            importPriceButton=True if importPriceButton == 'True' else False,
            importInventoryUnit=importInventoryUnit,
            importInventoryInterval=importInventoryInterval,
            importPriceUnit=importPriceUnit,
            importPriceInterval=importPriceInterval,
        )
        return res

    def getCredentials(self):
        currentCompany = self.env.company
        bellonaCredentials = self.env['bellona.credentials'].search([('company_id', '=', currentCompany.id),
                                                                       ('active', '=', True), ('token', '!=', None)])
        if len(bellonaCredentials.ids) > 1:
            raise ValidationError("Multiple Credentials are active for current company. Please select/active only one at a time.")
        elif len(bellonaCredentials.ids) == 0:
            raise ValidationError("No credential is assign to current company. Please go to Bellona->Credentials.")
        else:
            return bellonaCredentials.token

    def getBaseURL(self):
        return "https://eximapi.bellona.com.tr/"


    #Beloona Shipments
    def importBellonaInventory(self):
        token = self.getCredentials()
        url = self.getBaseURL() + "api/Material/SearchInventory"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }
        payload = json.dumps(False)
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            shipments = json.loads(response.content)
            print("import inventory",shipments)
            self.createShipments(shipments)
            self.env.cr.commit()
        else:
            currentCompany = self.env.company
            bellonaCredentials = self.env['bellona.credentials'].search([('company_id', '=', currentCompany.id),
                                                                         ('active', '=', True)], limit=1)
            bellonaCredentials.state = 'disconnect'

    def createShipments(self, shipments):
        for shipment in shipments:
            shipment_obj = self.env['bellona.shipments'].search([('saleS_ORDER', '=', shipment['saleS_ORDER']),('previouS_ORDER', '=', shipment['previouS_ORDER']),('productref', '=', shipment['productref'])])
            product_template = self.env['product.template'].search([('default_code', '=', shipment['productcode'])],limit=1)
            if not shipment_obj:
                shipment_obj.create({
                    'productcode': shipment['productcode'],
                    'product_template': product_template.id,
                    'ordeR_QUANTITY': shipment['ordeR_QUANTITY'],
                    'stocK_QUANTITY': shipment['stocK_QUANTITY'],
                    'customerref': shipment['customerref'],
                    'productref': shipment['productref'],
                    'packagenum': shipment['packagenum'],
                    'maktX_TR': shipment['maktX_TR'],
                    'maktX_EN': shipment['maktX_EN'],
                    'volum': shipment['volum'],
                    'audat': shipment['audat'],
                    'stawn': shipment['stawn'],
                    'saleS_ORDER': shipment['saleS_ORDER'],
                    'saleS_ORDER_POSNR': shipment['saleS_ORDER_POSNR'],
                    'balancE_QUANTITY': shipment['balancE_QUANTITY'],
                    'materiaL_TEXT': shipment['materiaL_TEXT'],
                    'previouS_ORDER': shipment['previouS_ORDER'],
                    'materiaL_VOLUM': shipment['materiaL_VOLUM'],
                    'customerbarcode': shipment['customerbarcode'],
                    'previouS_ORDER_POS': shipment['previouS_ORDER_POS'],
                    'producT_STOCK': shipment['producT_STOCK'],
                })

            else:
                shipment_obj.write({
                    'productcode': shipment['productcode'],
                    'product_template': product_template.id,
                    'ordeR_QUANTITY': shipment['ordeR_QUANTITY'],
                    'stocK_QUANTITY': shipment['stocK_QUANTITY'],
                    'customerref': shipment['customerref'],
                    'productref': shipment['productref'],
                    'packagenum': shipment['packagenum'],
                    'maktX_TR': shipment['maktX_TR'],
                    'maktX_EN': shipment['maktX_EN'],
                    'volum': shipment['volum'],
                    'audat': shipment['audat'],
                    'stawn': shipment['stawn'],
                    'saleS_ORDER': shipment['saleS_ORDER'],
                    'saleS_ORDER_POSNR': shipment['saleS_ORDER_POSNR'],
                    'balancE_QUANTITY': shipment['balancE_QUANTITY'],
                    'materiaL_TEXT': shipment['materiaL_TEXT'],
                    'previouS_ORDER': shipment['previouS_ORDER'],
                    'materiaL_VOLUM': shipment['materiaL_VOLUM'],
                    'customerbarcode': shipment['customerbarcode'],
                    'previouS_ORDER_POS': shipment['previouS_ORDER_POS'],
                    'producT_STOCK': shipment['producT_STOCK'],
                })

    #Bellona Materials
    def importMaterials(self):
        token = self.getCredentials()
        url = self.getBaseURL() + "api/Material/SearchMaterial"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }
        odooProducts = self.env['product.template'].search([('default_code', '!=', False)])
        for odooProduct in odooProducts:
            data = {
                "matnr": odooProduct.default_code,
                "date": "2022-01-07"
            }
            payload = json.dumps(data)
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                products = json.loads(response.content)
                print("Material response",products)
                self.createMaterials(products)
            else:
                currentCompany = self.env.company
                bellonaCredentials = self.env['bellona.credentials'].search([('company_id', '=', currentCompany.id),
                                                                             ('active', '=', True)], limit=1)
                bellonaCredentials.state = 'disconnect'
            self.env.cr.commit()

    def createMaterials(self, materials):
        for material in materials:
            odooMaterials = self.env['bellona.material'].search([('matnr', '=', material['matnr'])])
            odooProduct = self.env['product.template'].search([('matnr', '=', material['matnr'])])
            if not odooMaterials:
                odooMaterials = self.env['bellona.material'].create({
                    'matnr': material['matnr'],
                    'meins': material['meins'],
                    'ersda': material['ersda'],
                    'zzextwg': material['zzextwg'],
                    'mtpos': material['mtpos'],
                    'prodh': material['prodh'],
                    'vtexT_TR': material['vtexT_TR'],
                    'vtexT_EN': material['vtexT_EN'],
                    'ntgew': material['ntgew'],
                    'zZ_BDTINGTNM': material['zZ_BDTINGTNM'],
                    'zbdT_MLZTANIM': material['zbdT_MLZTANIM'],
                    'zzbolG15': material['zzbolG15'],
                    'e_MODEL_T': material['e_MODEL_T'],
                    'e_UNITE_T': material['e_UNITE_T'],
                    'brgew': material['brgew'],
                    'zzbdT_KAPADEDI': material['zzbdT_KAPADEDI'],
                    'volum': material['volum'],
                    'vmstd': material['vmstd'],
                    'vmsta': material['vmsta'],
                    'zbdT_KARTELA': material['zbdT_KARTELA'],
                    'zbdT_URETICI': material['zbdT_URETICI'],
                    'mvgR1': material['mvgR1'],
                    'zzbolG14': material['zzbolG14'],
                    'zzbolG13': material['zzbolG13'],
                    'zzbolG12': material['zzbolG12'],
                    'zzbolG11': material['zzbolG11'],
                    'zzbolG10': material['zzbolG10'],
                    'zzbolG09': material['zzbolG09'],
                    'zzbolG08': material['zzbolG08'],
                    'zzbolG02': material['zzbolG02'],
                    'zzbolG03': material['zzbolG03'],
                    'zzbolG04': material['zzbolG04'],
                    'zzbolG05': material['zzbolG05'],
                    'zzbolG06': material['zzbolG06'],
                    'maktx': material['maktx'],
                    'e_EXTWG_E': material['e_EXTWG_E'],
                    'e_FLART_E': material['e_FLART_E'],
                    'e_UNITE_E': material['e_UNITE_E'],
                    'e_MODEL_E': material['e_MODEL_E'],
                    'e_EXTWG_T': material['e_EXTWG_T'],
                    'e_FLART_T': material['e_FLART_T'],
                })
                odooProduct.write({
                    'bellona_material_ids': [[4, odooMaterials.id]]
                })
            else:
                odooMaterials.write({
                    'matnr': material['matnr'],
                    'meins': material['meins'],
                    'ersda': material['ersda'],
                    'zzextwg': material['zzextwg'],
                    'mtpos': material['mtpos'],
                    'prodh': material['prodh'],
                    'vtexT_TR': material['vtexT_TR'],
                    'vtexT_EN': material['vtexT_EN'],
                    'ntgew': material['ntgew'],
                    'zZ_BDTINGTNM': material['zZ_BDTINGTNM'],
                    'zbdT_MLZTANIM': material['zbdT_MLZTANIM'],
                    'zzbolG15': material['zzbolG15'],
                    'e_MODEL_T': material['e_MODEL_T'],
                    'e_UNITE_T': material['e_UNITE_T'],
                    'brgew': material['brgew'],
                    'zzbdT_KAPADEDI': material['zzbdT_KAPADEDI'],
                    'volum': material['volum'],
                    'vmstd': material['vmstd'],
                    'vmsta': material['vmsta'],
                    'zbdT_KARTELA': material['zbdT_KARTELA'],
                    'zbdT_URETICI': material['zbdT_URETICI'],
                    'mvgR1': material['mvgR1'],
                    'zzbolG14': material['zzbolG14'],
                    'zzbolG13': material['zzbolG13'],
                    'zzbolG12': material['zzbolG12'],
                    'zzbolG11': material['zzbolG11'],
                    'zzbolG10': material['zzbolG10'],
                    'zzbolG09': material['zzbolG09'],
                    'zzbolG08': material['zzbolG08'],
                    'zzbolG02': material['zzbolG02'],
                    'zzbolG03': material['zzbolG03'],
                    'zzbolG04': material['zzbolG04'],
                    'zzbolG05': material['zzbolG05'],
                    'zzbolG06': material['zzbolG06'],
                    'maktx': material['maktx'],
                    'e_EXTWG_E': material['e_EXTWG_E'],
                    'e_FLART_E': material['e_FLART_E'],
                    'e_UNITE_E': material['e_UNITE_E'],
                    'e_MODEL_E': material['e_MODEL_E'],
                    'e_EXTWG_T': material['e_EXTWG_T'],
                    'e_FLART_T': material['e_FLART_T'],
                })
                odooProduct.write({
                    'bellona_material_ids': [[4, odooMaterials.id]]
                })

    def importPrice(self):
        token = self.getCredentials()
        url = self.getBaseURL() + "api/Material/SearchPrice"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }
        odooProducts = self.env['product.template'].search([('default_code', '!=', False)])
        for odooProduct in odooProducts:
            payload = json.dumps(odooProduct.default_code)
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                product = json.loads(response.content)
                self.updatePrice(odooProduct, product)
            else:
                currentCompany = self.env.company
                bellonaCredentials = self.env['bellona.credentials'].search([('company_id', '=', currentCompany.id),
                                                                             ('active', '=', True)], limit=1)
                bellonaCredentials.state = 'disconnect'
        self.env.cr.commit()

    def updatePrice(self, odooProduct, product):
        odooProduct.write({
            'list_price': product[0]['biriM_FIYAT']
        })
        shipment_obj = self.env['bellona.shipments'].search([('productcode', '=', odooProduct.default_code)])
        if shipment_obj:
            for shipment in shipment_obj:
                shipment.maktx = product[0]['maktx']
                shipment.datab = product[0]['datab']
                shipment.datbi = product[0]['datbi']
                shipment.konwa = product[0]['konwa']
                shipment.kbetr = product[0]['kbetr']
                shipment.kpein = product[0]['kpein']
                shipment.biriM_FIYAT = product[0]['biriM_FIYAT']

class BeloonaShiment(models.Model):
    _name = 'bellona.shipments'


    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    productcode = fields.Char('productcode')
    product_template = fields.Many2one('product.template','Product Template')
    ordeR_QUANTITY = fields.Char('ordeR_QUANTITY')
    stocK_QUANTITY = fields.Char('stocK_QUANTITY')
    customerref  = fields.Char('customerref')
    productref = fields.Char('productref')
    packagenum = fields.Char('packagenum')
    maktX_TR = fields.Char('maktX_TR')
    maktX_EN  = fields.Char('maktX_EN')
    volum=  fields.Char('volum')
    audat = fields.Char('audat')
    stawn = fields.Char('stawn')
    saleS_ORDER = fields.Char('saleS_ORDER')
    saleS_ORDER_POSNR = fields.Char('saleS_ORDER_POSNR')
    balancE_QUANTITY = fields.Char('balancE_QUANTITY')
    materiaL_TEXT = fields.Char('materiaL_TEXT')
    previouS_ORDER = fields.Char('previouS_ORDER')
    materiaL_VOLUM = fields.Char('materiaL_VOLUM')
    customerbarcode = fields.Char('customerbarcode')
    previouS_ORDER_POS = fields.Char('previouS_ORDER_POS')
    producT_STOCK = fields.Char('producT_STOCK')
    maktx = fields.Char('maktx')
    datab = fields.Char('datab')
    datbi = fields.Char('datbi')
    kbetr = fields.Char('kbetr')
    kpein = fields.Char('kpein')
    biriM_FIYAT = fields.Char('biriM_FIYAT')
    konwa = fields.Char('konwa')


class BeloonaMaterial(models.Model):
    _name = 'bellona.material'


    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    matnr = fields.Char('matnr')
    zbdT_MLZTANIM = fields.Char('zbdT_MLZTANIM')
    zZ_BDTINGTNM = fields.Char('zZ_BDTINGTNM')
    ntgew = fields.Char('ntgew')
    vtexT_EN = fields.Char('vtexT_EN')
    vtexT_TR = fields.Char('vtexT_TR')
    prodh = fields.Char('prodh')
    mtpos = fields.Char('mtpos')
    zzextwg = fields.Char('zzextwg')
    ersda = fields.Char('ersda')
    meins = fields.Char('meins')
    mvgR1 = fields.Char('mvgR1')
    zbdT_URETICI = fields.Char('zbdT_URETICI')
    zbdT_KARTELA = fields.Char('zbdT_KARTELA')
    vmsta = fields.Char('vmsta')
    vmstd = fields.Char('vmstd')
    volum = fields.Char('volum')
    zzbdT_KAPADEDI = fields.Char('zzbdT_KAPADEDI')
    brgew = fields.Char('brgew')
    e_UNITE_T = fields.Char('e_UNITE_T')
    e_MODEL_T = fields.Char('e_MODEL_T')
    zzbolG15 = fields.Char('zzbolG15')
    zzbolG14 = fields.Char('zzbolG14')
    zzbolG13 = fields.Char('zzbolG13 ')
    zzbolG12 = fields.Char('zzbolG12')
    zzbolG11 = fields.Char('zzbolG11')
    zzbolG10 = fields.Char('zzbolG10')
    zzbolG09 = fields.Char('zzbolG09')
    zzbolG08 = fields.Char('zzbolG08' )
    zzbolG07= fields.Char('zzbolG07')
    zzbolG06 = fields.Char('zzbolG06')
    zzbolG05 = fields.Char('zzbolG05')
    zzbolG04 = fields.Char('zzbolG04')
    zzbolG03 = fields.Char('zzbolG03')
    zzbolG02 = fields.Char('zzbolG02')
    maktx = fields.Char('maktx')
    e_EXTWG_E = fields.Char('e_EXTWG_E')
    e_FLART_E = fields.Char('e_FLART_E')
    e_UNITE_E = fields.Char('e_UNITE_E')
    e_MODEL_E = fields.Char('e_MODEL_E')
    e_EXTWG_T = fields.Char('e_EXTWG_T')
    e_FLART_T = fields.Char('e_FLART_T')