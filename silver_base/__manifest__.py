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
            # Librerías Externas (Leaflet + Geosearch)
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
            'https://unpkg.com/leaflet-geosearch@3.11.0/dist/geosearch.css',
            'https://unpkg.com/leaflet-geosearch@3.11.0/dist/bundle.min.js',
            
            # Tu Widget
            'silver_base/static/src/components/silver_map_widget/silver_map_widget.xml',
            'silver_base/static/src/components/silver_map_widget/silver_map_widget.js',

            # Record Link Widget
            'silver_base/static/src/components/record_link/record_link.js',
            'silver_base/static/src/components/record_link/record_link.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}