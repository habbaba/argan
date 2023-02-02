{
    'name': 'Advanced List Search',
    'version': '15.0.1.1.0',
    'category': 'Tools',
    'summary': 'Module for advanced list search',
    'author': 'Opsway',
    'website': 'https://opsway.com',
    'depends': [
        'base_setup',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'assets': {
        'web.assets_backend': [
            'advance_list_search/static/src/js/*.js',
            'advance_list_search/static/src/scss/*.scss',
        ],
        'web.assets_qweb': [
            'advance_list_search/static/src/xml/templates.xml',
        ],
    },
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
