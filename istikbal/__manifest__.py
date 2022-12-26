# -*- coding: utf-8 -*-
{
    'name': "Istikbal Integration",

    'summary': """
       Istikbal Integration with odoo 
       Import Shipment, Import inventory,Import sales order analysis,Import Materials.""",

    'description': """
        Istikbal Integration with odoo 
       Import Shipment, Import inventory,Import sales order analysis,Import Materials.
    """,

    'author': "HAKSolutions",
    'website': "http://www.HAKSolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.5',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['stock','sale','purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/import_schedule.xml',
        'views/res_config_settings.xml',
        'views/istikbal_settings.xml',
        'views/product_template.xml',
        'views/shipments.xml',
        'views/barcodes.xml',
    ],
}
