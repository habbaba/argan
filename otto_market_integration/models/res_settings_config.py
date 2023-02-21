# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning, ValidationError
import logging
import requests
import json
from datetime import datetime, timedelta
import time
_logger = logging.getLogger(__name__)


class InheritRCSOtto(models.TransientModel):
    _inherit = 'res.config.settings'

    otto_token = fields.Char(string='Access Token')
    otto_refresh_token = fields.Char(string='Refresh Token')
    otto_expires_in = fields.Char(string='Expires In')
    otto_shipment_date_from = fields.Datetime("From Date", default=fields.Date.today(), config_parameter='otto_market_integration.otto_shipment_date_from')

    def otto_get_credentials_type(self):
        currentCompany = self.env.company
        ottoCredentials = self.env['otto.credentials'].search([('company_id', '=', currentCompany.id),
                                                                       ('active', '=', True)])
        if len(ottoCredentials.ids) > 1:
            raise ValidationError("Multiple Credentials are active for current company. Please select/active only one at a time.")
        elif len(ottoCredentials.ids) == 0:
            raise ValidationError("No credential is assign to current company. Please go to Istikbal/Credentials.")
        else:
            return ottoCredentials.otto_credentials_type

    def otto_request_essentials(self):
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        self.otto_token_expiry_check()
        otto_token = IrConfigParameter.get_param('otto_market_integration.otto_token')
        otto_credentials_type = self.otto_get_credentials_type()
        return otto_token, otto_credentials_type

    def otto_import_brands(self):
        try:
            otto_token, otto_credentials_type = self.otto_request_essentials()

            headers = {
                'Authorization': 'Bearer ' + otto_token
            }
            page_number = 0
            while True:
                url = otto_credentials_type + "/v3/products/brands?limit=2000&page=" + str(page_number)
                response = requests.request("GET", url, headers=headers)
                if response.status_code == 200:
                    brand_response = json.loads(response.text)
                    if len(brand_response['brands']) > 0:
                        self.otto_create_brands(brand_response['brands'])
                    else:
                        break
                else:
                    break
                page_number += 1
            self.env.cr.commit()
        except Exception as e:
            raise ValidationError(e)

    def otto_create_brands(self, brands):
        try:
            for brand in brands:
                odooBrand = self.env['otto.brand'].search([('otto_id', '=', brand['id'])])
                if not odooBrand:
                    self.env['otto.brand'].create({
                        'otto_id': brand['id'],
                        'otto_name': brand['name']
                    })
                else:
                    odooBrand.write({
                        'otto_id': brand['id'],
                        'otto_name': brand['name']
                    })
        except Exception as e:
            raise ValidationError(e)

    def otto_import_categories(self):
        try:
            otto_token, otto_credentials_type = self.otto_request_essentials()

            headers = {
                'Authorization': 'Bearer ' + otto_token
            }
            page_number = 0
            while True:
                url = otto_credentials_type + "/v3/products/categories?limit=2000&page=" + str(page_number)
                response = requests.request("GET", url, headers=headers)
                if response.status_code == 200:
                    categories_response = json.loads(response.text)
                    if len(categories_response['categoryGroups']) > 0:
                        self.otto_create_categories(categories_response['categoryGroups'])
                    else:
                        break
                else:
                    break
                page_number += 1
            self.env.cr.commit()
        except Exception as e:
            raise ValidationError(e)

    def otto_create_categories(self, categories_groups):
        for categories_group in categories_groups:
            odooCategoryGroup = self.env['otto.category.group'].search([('otto_name', '=', categories_group['categoryGroup'])])
            if not odooCategoryGroup:
                odooCategoryGroup = self.env['otto.category.group'].create({
                    'otto_name': categories_group['categoryGroup']
                })
            self.otto_create_child_categories(categories_group['categories'], odooCategoryGroup)

    def otto_create_child_categories(self, categories, odooParentCategory):
        for category in categories:
            odooChildCategory = self.env['product.category'].search([('name', '=', category)])
            if not odooChildCategory:
                odooChildCategory = self.env['product.category'].create({
                    'name': category,
                    'otto_category_group_id': odooParentCategory.id
                })
            else:
                odooChildCategory.write({
                    'name': category,
                    'otto_category_group_id': odooParentCategory.id
                })

    def otto_import_products(self):
        try:
            otto_token, otto_credentials_type = self.otto_request_essentials()

            headers = {
                'Authorization': 'Bearer ' + otto_token
            }
            page_number = 0
            while True:
                url = otto_credentials_type + "/v3/products?limit=2000&page=" + str(page_number)
                response = requests.request("GET", url, headers=headers)
                if response.status_code == 200:
                    products_response = json.loads(response.text)
                    if len(products_response['productVariations']) > 0:
                        self.otto_create_products(products_response['productVariations'])
                    else:
                        break
                else:
                    break
                page_number += 1
            self.env.cr.commit()
        except Exception as e:
            raise ValidationError(e)

    def otto_create_products(self, products, fromOrder=False):
        for product in products:
            odooCategory = self.env['product.category'].search([('name', '=', product['productDescription']['category'])])
            odooBrand = self.env['otto.brand'].search([('otto_id', '=', product['productDescription']['brandId'])])

            odooProductTemplate = self.env['product.template'].search([('default_code', '=', product['sku'])])
            if not odooProductTemplate:
                odooProductTemplate = self.env['product.template'].create({
                    'name': product['productReference'],
                    'default_code': product['sku'],
                    'categ_id': odooCategory.id if odooCategory else None,
                    'otto_brand_id': odooBrand.id if odooBrand else None,
                    'description': product['productDescription']['description'],
                    'detailed_type': 'product'
                })
                product_product = self.env['product.product'].search(
                    [('product_tmpl_id', '=', odooProductTemplate.id)])
                if not product_product:
                    self.env['product.product'].create({
                        'product_tmpl_id': odooProductTemplate.id
                    })
            # if len(product['productDescription']['attributes']) > 0:
            #     self.otto_create_attributes(product['productDescription']['attributes'], odooProductTemplate)
            if fromOrder:
                return odooProductTemplate

    def otto_create_attributes(self, attributes, odooProductTemplate):
        for attribute in attributes:
            odooAttribute = self.env['product.attribute'].search([('name', '=', attribute['name'])])
            if not odooAttribute:
                odooAttribute = self.env['product.attribute'].create({
                    'name': attribute['name'],
                    'create_variant': 'dynamic'
                })
            values_list = []
            for value in attribute['values']:
                odooAttributeValue = self.env['product.attribute.value'].search([('name', '=', value), ('attribute_id', '=', odooAttribute.id)])
                if not odooAttributeValue:
                    odooAttributeValue = self.env['product.attribute.value'].create({
                        'name': value,
                        'attribute_id': odooAttribute.id,
                    })
                values_list.append(odooAttributeValue.id)

            self.env['product.template.attribute.line'].create({
                'product_tmpl_id': odooProductTemplate.id,
                'attribute_id': odooAttribute.id,
                'value_ids': [(6, 0, values_list)],
            })

    def otto_update_products_qty(self):
        try:
            # self.otto_token_expiry_check()
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            otto_token = IrConfigParameter.get_param('otto_market_integration.otto_token')
            otto_credentials_type = self.otto_get_credentials_type()
            headers = {
                'Authorization': 'Bearer ' + otto_token
            }
            page_number = 0
            while True:
                url = otto_credentials_type + "/v2/quantities?limit=2000&page=" + str(page_number)
                response = requests.request("GET", url, headers=headers)
                if response.status_code == 200:
                    quantities_response = json.loads(response.text)
                    if len(quantities_response['resources']) > 0:
                        if len(quantities_response['resources']['variations']) > 0:
                            self.otto_update_quantity(quantities_response['resources']['variations'])
                        else:
                            break
                    else:
                        break
                else:
                    break
                page_number += 1
            self.env.cr.commit()
        except Exception as e:
            raise ValidationError(e)

    def otto_update_quantity(self, products):
        for product in products:
            odooProduct = self.env['product.template'].search([('default_code', '=', product['sku'])])
            product_product = self.env['product.product'].search(
                [('product_tmpl_id', '=', odooProduct.id)])
            odooStock = self.env['stock.quant'].search([('product_id', '=', product_product.id)])
            if odooStock:
                odooStock.sudo().write({
                    'inventory_quantity': istikbal_product['quantity'],
                    'quantity': istikbal_product['quantity'],
                })
            else:
                odooLocation = self.env['stock.location'].search([('name', '=', 'Stock')])
                self.env['stock.quant'].sudo().create({
                    'inventory_quantity': istikbal_product['quantity'],
                    'quantity': istikbal_product['quantity'],
                    'product_id': odoo_product.id,
                    'location_id': odooLocation.id
                })

    def otto_import_orders(self):
        try:
            otto_token, otto_credentials_type = self.otto_request_essentials()

            headers = {
                'Authorization': 'Bearer ' + otto_token
            }
            url = otto_credentials_type + "/v4/orders"
            while True:
                response = requests.request("GET", url, headers=headers)
                if response.status_code == 200:
                    orders_response = json.loads(response.text)
                    if len(orders_response['resources']) > 0:
                        self.otto_create_orders(orders_response['resources'])
                    else:
                        break
                    if orders_response.get('links'):
                        pass
                    else:
                        break
                else:
                    break
            self.env.cr.commit()
        except Exception as e:
            raise ValidationError(e)

    def otto_create_orders(self, orders):
        for order in orders:
            if order.get('deliveryAddress'):
                odooOrder = self.env['sale.order'].search([('otto_order_id', '=', order['salesOrderId'])])
                orderCustomer = self.otto_get_customer(order['deliveryAddress'], order['invoiceAddress'])
                orderDate = datetime.strptime(order['orderDate'], '%Y-%m-%dT%H:%M:%S.%f%z').date()

                if not odooOrder:
                    odooOrder = self.env['sale.order'].create({
                        'otto_order_id': order['salesOrderId'],
                        "name": order["orderNumber"],
                        "partner_id": orderCustomer.id,
                        "state": 'sale',
                        "date_order": orderDate,
                    })
                else:
                    odooOrder.write({
                        'otto_order_id': order['salesOrderId'],
                        "name": order["orderNumber"],
                        "partner_id": orderCustomer.id,
                        "state": 'sale',
                        "date_order": orderDate,
                    })

                self.otto_create_order_line(order['positionItems'], odooOrder)

    def otto_create_order_line(self, lines, odooOrder):
        for line in lines:
            if line.get('product'):
                orderProduct = self.env['product.template'].search([('default_code', '=', line['product']['sku'])])
                if not orderProduct:
                    orderProduct = self.otto_get_order_line_product(line['product']['sku'])
                odoo_product = self.env['product.product'].search([('product_tmpl_id', '=', orderProduct.id)])[0]
                totalDiscount = 0

                totalAmount = line['itemValueGrossPrice']['amount']
                if line.get('itemValueDiscount'):
                    discountAmount = line['itemValueDiscount']['amount']
                    totalDiscount = (discountAmount / totalAmount) * 100
                self.env['sale.order.line'].create({
                    'product_id': odoo_product.id,
                    "order_id": odooOrder.id,
                    "product_uom_qty": 1,
                    'price_unit': totalAmount,
                    'discount': totalDiscount
                })

    def otto_get_order_line_product(self, sku):
        try:
            otto_token, otto_credentials_type = self.otto_request_essentials()

            headers = {
                'Authorization': 'Bearer ' + otto_token
            }
            url = otto_credentials_type + "/v3/products?sku" + str(sku)
            response = requests.request("GET", url, headers=headers)
            if response.status_code == 200:
                products_response = json.loads(response.text)
                if len(products_response['productVariations']) > 0:
                    return self.otto_create_products(products_response['productVariations'], True)
                self.env.cr.commit()
        except Exception as e:
            raise ValidationError(e)

    def otto_get_customer(self, deliveryAddress, invoiceAddress):
        partner = self.env['res.partner']
        name = deliveryAddress['salutation'] + " " + deliveryAddress['firstName'] + " " + deliveryAddress['lastName']
        odooCustomer = partner.search([('name', '=', name)])
        if not odooCustomer:
            odooCustomer = partner.create({
                'name': name,
                'customer_rank': 7,
            })
        self.otto_create_deliveryAddress(deliveryAddress, odooCustomer)
        self.otto_create_invoiceAddress(invoiceAddress, odooCustomer)
        return odooCustomer

    def otto_create_deliveryAddress(self, deliveryAddress, odooCustomer):
        partner = self.env['res.partner']
        odooCustomerDeliveryAddress = partner.search([('parent_id', '=', odooCustomer.id), ('zip', '=', deliveryAddress['zipCode'])])
        if not odooCustomerDeliveryAddress:
            odooCountry = self.env['res.country'].search([('code', '=', deliveryAddress['countryCode'])])
            street2 = None
            if deliveryAddress.get('addition'):
                street2 = deliveryAddress['addition']

            partner.create({
                'name': odooCustomer.name + " Delivery Address",
                'type': 'delivery',
                'street': deliveryAddress['street'],
                'street2': street2 + " " + deliveryAddress['houseNumber'] if street2 else deliveryAddress['houseNumber'],
                'city': deliveryAddress['city'],
                'zip': deliveryAddress['zipCode'],
                'country_id': odooCountry.id if odooCountry else None,
                'parent_id': odooCustomer.id
            })

    def otto_create_invoiceAddress(self, invoiceAddress, odooCustomer):
        partner = self.env['res.partner']
        odooCustomerDeliveryAddress = partner.search(
            [('parent_id', '=', odooCustomer.id), ('zip', '=', invoiceAddress['zipCode'])])
        if not odooCustomerDeliveryAddress:
            odooCountry = self.env['res.country'].search([('code', '=', invoiceAddress['countryCode'])])
            street2 = None
            if invoiceAddress.get('addition'):
                street2 = invoiceAddress['addition']
            partner.create({
                'name': odooCustomer.name + " Invoice Address",
                'type': 'delivery',
                'street': invoiceAddress['street'],
                'street2': street2 + " " + invoiceAddress['houseNumber'] if street2 else invoiceAddress['houseNumber'],
                'city': invoiceAddress['city'],
                'zip': invoiceAddress['zipCode'],
                'country_id': odooCountry.id if odooCountry else None,
                'parent_id': odooCustomer.id
            })

    def otto_import_shipments(self):
        try:
            otto_token, otto_credentials_type = self.otto_request_essentials()

            datefrom = str(datetime.strptime(IrConfigParameter.get_param('otto_market_integration.otto_shipment_date_from'), '%Y-%m-%d %H:%M:%S').date())
            headers = {
                'Authorization': 'Bearer ' + otto_token
            }
            url = otto_credentials_type + "/v1/shipments?datefrom=" + datefrom
            while True:
                response = requests.request("GET", url, headers=headers)
                if response.status_code == 200:
                    shipments_response = json.loads(response.text)
                    if len(shipments_response['resources']) > 0:
                        self.otto_create_shipments(shipments_response['resources'])
                    else:
                        break
                    if shipments_response.get('links'):
                        pass
                    else:
                        break
                else:
                    break
            self.env.cr.commit()
        except Exception as e:
            raise ValidationError(e)

    def otto_create_shipments(self, shipments):
        for shipment in shipments:
            otto_shipment = self.otto_get_shipment(shipment)
            if otto_shipment:
                if otto_shipment.get('positionItems'):
                    self.otto_create_stock_picking(otto_shipment)

    def otto_get_shipment(self, shipment):
        try:
            otto_token, otto_credentials_type = self.otto_request_essentials()

            headers = {
                'Authorization': 'Bearer ' + otto_token
            }
            url = otto_credentials_type + "/v1/shipments/" + shipment['shipmentId']
            response = requests.request("GET", url, headers=headers)
            if response.status_code == 200:
                shipment_response = json.loads(response.text)
                return shipment_response
            else:
                return None
        except Exception as e:
            raise ValidationError(e)

    def otto_token_expiry_check(self):
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            otto_expires_in = IrConfigParameter.get_param('otto_market_integration.otto_expires_in')
            expires_in = datetime.fromtimestamp(int(otto_expires_in) / 1e3)
            expires_in = expires_in + timedelta(seconds=1800)
            now = datetime.now()
            if now > expires_in:
                self.otto_generate_refresh_token()
        except Exception as e:
            raise ValidationError(str(e))

    def otto_generate_refresh_token(self):
        """
        Refresh OTTO Token for API
        :return:
        """
        try:
            IrConfigParameter = self.env['ir.config_parameter'].sudo()
            otto_refresh_token = IrConfigParameter.get_param('otto_market_integration.otto_refresh_token')
            otto_credentials_type = self.otto_get_credentials_type()
            url = otto_credentials_type + "/v1/token"

            payload = 'refresh_token=%s&grant_type=refresh_token&client_id=token-otto-api' % (otto_refresh_token)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cache-Control': 'no-cache'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            if response.status_code == 200:
                token_response = json.loads(response.text)
                IrConfigParameter.set_param('otto_market_integration.otto_token', token_response['access_token'])
                IrConfigParameter.set_param('otto_market_integration.otto_refresh_token', token_response['refresh_token'])
                IrConfigParameter.set_param('otto_market_integration.otto_expires_in', int(round(time.time() * 1000)))
        except Exception as e:
            raise ValidationError(e)

    def action_of_button(self, name, message):
        message_id = self.env['message.wizard'].create({
            'text': message,
        })
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'res_id': message_id.id,
            'target': 'new',
        }
