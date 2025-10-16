{
    'name': 'Silver Base',
    'version': '17.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Silver Base module for SilverOdoo',
    'author': 'SilverData',
    'website': 'https://www.silverdata.org',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
    ],
    'data': [ 
        'security/ir.model.access.csv',
        'views/silver_zone_views.xml',
        'views/silver_address_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'silver_base/static/src/css/general.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}

