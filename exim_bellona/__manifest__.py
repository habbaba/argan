# -*- coding: utf-8 -*-
{
    'name': "Bellona Connector",

    'summary': """
       Bellona Integration with odoo
       1.Import shipments
       2.Import material
       3.Import Inventory
       4.Import BOM
       5.Import Price
       https://www.loom.com/share/296b682aa14d49c8a680878ff8414caa
       """,

    'description': """
        Long description of module's purpose
    """,

    'author': "HAK solutions",
    'website': "http://www.hasksolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['stock','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/bellona_settings.xml',
        'views/res_config_settings.xml',
        'data/import_schedulers.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
