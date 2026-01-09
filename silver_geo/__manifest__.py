{
    'name': 'Silver GEO',
    'version': '19.0.1.0.0',
    'category': 'Geolocation',
    'summary': 'Geolocation features for Silver Odoo',
    'depends': ['silver_network', 'silver_base'],
    'data': [
        'views/silver_map_views.xml',
        'views/silver_address_views.xml',
        'views/menus.xml',
  #      'views/silver_node_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Leaflet Assets for the map widget
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
            
            'silver_geo/static/src/css/map_view.css',
            'silver_geo/static/src/js/map_view.js',
            'silver_geo/static/src/xml/map_view.xml',
            
            # Coordinate Picker Assets
            'silver_geo/static/src/css/coordinate_picker.css',
            'silver_geo/static/src/js/coordinate_picker_map.js',
            'silver_geo/static/src/xml/coordinate_picker_map.xml',

            # Node Map Widget
            'silver_geo/static/src/js/node_map_widget.js',
            'silver_geo/static/src/xml/node_map_widget.xml',
        ],
    },
    'installable': True,
    'application': False,
}
