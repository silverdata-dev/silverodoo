{
    'name': 'Silver GEO',
    'version': '1.0',
    'category': 'Geolocation',
    'summary': 'Geolocation features for Silver Odoo',
    'depends': ['silver_network'],
    'data': [
        'views/silver_map_views.xml',
        'views/menus.xml',
        'views/silver_node_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'silver_geo/static/src/css/map_view.css',
            'silver_geo/static/src/js/map_view.js',
            'silver_geo/static/src/xml/map_view.xml',
            # Coordinate Picker Assets
            #   'silver_geo/static/src/js/coordinate_picker_map.js',
            #    'silver_geo/static/src/xml/coordinate_picker_map.xml',
        ],
    },
    'installable': True,
    'application': False,
}
