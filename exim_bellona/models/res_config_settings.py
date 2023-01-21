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


    def getBellonaCredentials(self):
        currentCompany = self.env.company
        bellonaCredentials = self.env['bellona.credentials'].search([('company_id', '=', currentCompany.id),
                                                                       ('active', '=', True), ('token', '!=', None)])

        if len(bellonaCredentials.ids) > 1:
            raise ValidationError("Multiple Credentials are active for current company. Please select/active only one at a time.")
        elif len(bellonaCredentials.ids) == 0:
            raise ValidationError("No credential is assign to current company. Please go to Bellona->Credentials.")
        else:
            bellonaCredentials.connect_bellona_credentials()
            return bellonaCredentials.token

    def getBaseURL(self):
        return "https://eximapi.bellona.com.tr/"


    #Beloona Shipments
    def importBellonaInventory(self):
        token = self.getBellonaCredentials()
        url = self.getBaseURL() + "api/Material/SearchInventory"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }
        payload = json.dumps(False)
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            shipments = json.loads(response.content)
            self.createShipments(shipments)
            self.env.cr.commit()
        else:
            raise UserError(_('Error %s .', response))

    def createShipments(self, shipments):
        for shipment in shipments:
            shipment_obj = self.env['bellona.shipments'].search([('saleS_ORDER', '=', shipment['saleS_ORDER']),('saleS_ORDER_POSNR', '=', shipment['saleS_ORDER_POSNR']),('productref', '=', shipment['productref']),('company_id', '=', self.env.company.id)])
            product_template = self.env['product.template'].search([('default_code', '=', shipment['productcode']),('company_id', '=', self.env.company.id)],limit=1)
            if not shipment_obj:
                shipment_obj = self.env['bellona.shipments'].create({
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
                shipment_obj = self.env['bellona.shipments'].write({
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
       
            purchase_order = self.env['purchase.order'].search([('name', '=', shipment['customerbarcode'])],limit=1)
            if purchase_order:
                sale_order = self.env['sale.order'].search([('name', '=', purchase_order.origin)], limit=1)
                purchase_order.bellona_shipments=[(4,shipment_obj.id)]
                if sale_order:
                    sale_order.bellona_shipments = [(4,shipment_obj.id)]
    #Bellona Materials
    def importBellonaMaterials(self):
        token = self.getBellonaCredentials()
        url = self.getBaseURL() + "api/Material/SearchMaterial"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }
        

     
        data = {

              "date": "2022-10-01"
        }
        payload = json.dumps(data)
        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            products = json.loads(response.content)
            # print("Material response",products)
            self.createBellonaMaterials(products)
        else:
            raise UserError(_('Error %s .', response))

        self.env.cr.commit()

    def createBellonaMaterials(self, materials):
        for material in materials:
            odooMaterials = self.env['bellona.material'].search([('matnr', '=', material['matnr']),('company_id', '=', self.env.company.id)])
            odooProduct = self.env['product.template'].search([('default_code', '=', material['matnr']),('company_id', '=', self.env.company.id)],limit=1)
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
        token = self.getBellonaCredentials()
        url = self.getBaseURL() + "api/Material/SearchPrice"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }
        odooProducts = self.env['product.template'].search([('default_code', '!=', False),('company_id', '=', self.env.company.id)])
        for odooProduct in odooProducts:
            payload = json.dumps(odooProduct.default_code)
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                product = json.loads(response.content)
                self.updatePrice(odooProduct, product)
            else:
                raise UserError(_('Coach of Error %s .', response))
        self.env.cr.commit()

    def updatePrice(self, odooProduct, product):
        odooProduct.write({
            'standard_price': product[0]['biriM_FIYAT']
        })
        shipment_obj = self.env['bellona.shipments'].search([('productcode', '=', odooProduct.default_code),('company_id', '=', self.env.company.id)])
        material_obj = self.env['bellona.material'].search([('matnr', '=', odooProduct.default_code),('company_id', '=', self.env.company.id)],limit=1)
        if shipment_obj:
            for shipment in shipment_obj:
                shipment.maktx = product[0]['maktx']
                shipment.datab = product[0]['datab']
                shipment.datbi = product[0]['datbi']
                shipment.konwa = product[0]['konwa']
                shipment.kbetr = product[0]['kbetr']
                shipment.kpein = product[0]['kpein']
                shipment.biriM_FIYAT = product[0]['biriM_FIYAT']
        if  material_obj:
            material_obj.maktx = product[0]['maktx']
            material_obj.datab = product[0]['datab']
            material_obj.datbi = product[0]['datbi']
            material_obj.konwa = product[0]['konwa']
            material_obj.kbetr = product[0]['kbetr']
            material_obj.kpein = product[0]['kpein']
            material_obj.biriM_FIYAT = product[0]['biriM_FIYAT']

        # Beloona Shipments

    def importBellonaBom(self):
        token = self.getBellonaCredentials()
        url = self.getBaseURL() + "api/Material/SearchBOM"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token,
        }
        data = {
            "material": "20ECT1R00500026"

        }
        payload = json.dumps(data)
        response = requests.request("POST", url, headers=headers, data=payload)
        # print( "response",response)
        if response.status_code == 200:
            boms = json.loads(response.content)
            # print("Boms", boms)
            self.createBoms(boms)
            self.env.cr.commit()
        else:
            raise UserError(_('Coach of Error %s .', response))






class BeloonaShiment(models.Model):
    _name = 'bellona.shipments'
    _description = "Bellona Shipments"
    _rec_name = 'productcode'


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
    purchase_id = fields.Many2one('purchase.order',compute="compute_the_purchase_id")




    def compute_the_purchase_id(self):
        for i in self:
            po = self.env['purchase.order'].search([("name", '=', i.customerbarcode)], limit=1)
            i.purchase_id=po.id





    def confirm_purchase_receipt(self):
        for i in self:
            po=self.env['purchase.order'].search([("name",'=',i.customerbarcode)],limit=1)
            for k in po.picking_ids:
                if k.state not in ['cancel','done']:
                    k.button_validate()

class BeloonaMaterial(models.Model):
    _name = 'bellona.material'
    _description = "Bellona Material"
    _rec_name = 'matnr'


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
    e_EXTWG_E = fields.Char('e_EXTWG_E')
    e_FLART_E = fields.Char('e_FLART_E')
    e_UNITE_E = fields.Char('e_UNITE_E')
    e_MODEL_E = fields.Char('e_MODEL_E')
    e_EXTWG_T = fields.Char('e_EXTWG_T')
    e_FLART_T = fields.Char('e_FLART_T')
    maktx = fields.Char('maktx')
    datab = fields.Char('datab')
    datbi = fields.Char('datbi')
    kbetr = fields.Char('kbetr')
    kpein = fields.Char('kpein')
    biriM_FIYAT = fields.Char('biriM_FIYAT')
    konwa = fields.Char('konwa')
    product_template = fields.Many2one('product.template', 'Product Template')

class BeloonaBOM(models.Model):
    _name = 'bellona.bom'
    _description = "Bellona Bom"
    _rec_name = 'matnr'


    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    matnr = fields.Char('matnr')
