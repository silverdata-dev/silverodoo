{
    'name': 'Silver CRM',
    'version': '17.0.1.0.0',
    'summary': 'Adaptaciones de CRM para Silver ISP',
    'description': """
        - Añade campos y lógica para la gestión de contratos de ISP desde las oportunidades.
        - Integra un asistente para la búsqueda de nodos de red cercanos.
        - Añade un mapa interactivo para la selección de cajas NAP.
    """,
    'author': 'Gemini',
    'website': 'https://www.google.com',
    'category': 'Sales/CRM',
    'depends': ['crm', 'silver_contract', 'silver_network', 'silver_geo'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
        'views/nap_map_selector_views.xml',
        'wizard/find_node_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'silver_crm/static/src/js/nap_map_selector_view.js',
            'silver_crm/static/src/xml/nap_map_selector_templates.xml',
        ],
    },
    'installable': True,
    'application': True,
}
