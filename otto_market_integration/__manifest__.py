# -*- coding: utf-8 -*-
{
    'name': "Otto Market",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'sale_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_settings_config.xml',
        'views/otto_market_settings.xml',
        'views/product_brand.xml',
        'views/product_category_group.xml',
        'views/product_category.xml',
        'views/product_template.xml',
        'wizard/message_wizard.xml',
    ],
}
