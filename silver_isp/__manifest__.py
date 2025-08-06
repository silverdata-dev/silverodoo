{
    'name': 'Silver ISP',
    'version': '17.0.1.0.0',
    'summary': 'Módulo para la gestión de ISP',
    'description': 'Módulo extraído de un archivo de texto para la gestión de Nodos y Equipos Core de un ISP.',
    'category': 'Services/Telecommunication',
    'author': 'Gemini',
    'website': '',
    'license': 'AGPL-3',
    'depends': ['base', 'mail', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/isp_views.xml',
    ],
    'installable': True,
    'application': True,
}
