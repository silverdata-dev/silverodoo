{
    'name': 'Silver UNMS Calendar',
    'version': '17.0.1.0.0',
'icon': 'static/description/icon.png',
    'category': 'Productivity',
    'summary': 'Calendario tipo UNMS para agendamiento de oportunidades',
    'description': """
        Este módulo implementa una vista de calendario tipo línea de tiempo (Timeline)
        para gestionar la agenda de instaladores por zona.
        
        Características:
        - Vista Timeline basada en web_timeline.
        - Agrupación por Zona y luego por Instalador (User).
        - Drag & Drop de Oportunidades (CRM Leads).
    """,
    'author': 'SilverData',
    'depends': ['base', 'crm', 'web_timeline', 'silver_base', 'silver_crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
        'views/silver_assignment_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
}
