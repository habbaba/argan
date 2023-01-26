# -*- coding: utf-8 -*-
{
    'name' : "Advance Payment for Sale and Purchase",
    "author": "HAK Technologies",
    'version': '15.0.1.1',
    "images":['static/description/icon.png'],
    'summary': 'Advance Payment for Sale and Purchase',
    'description' : """Advance Payment for Sale and Purchase""",
    "license" : "OPL-1",
    'depends' : ['sale_management','purchase','account'],
    'data': [
                'security/advance_payment_group.xml',
                'security/ir.model.access.csv',
                'views/res_config_view.xml',
                'views/sale_order_view.xml',
                'views/purchase_order_view.xml',
                'wizard/sale_advance_payment_wizard.xml',
                'wizard/purchase_advance_payment_wizard.xml',
             ],
    'installable': True,
    'auto_install': False,
    'category': 'Accounting',
}
