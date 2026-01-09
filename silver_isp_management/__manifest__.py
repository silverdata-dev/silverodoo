{
    'name': 'Silver ISP Management',
    'version': '19.0.1.0.0',
    'summary': 'Módulo para la gestión de contratos, clientes y equipos para un ISP.',
    'author': 'SilverData',
    'website': 'https://www.silver-data.net',
    'license': 'AGPL-3',
    'category': 'Services/Telecommunications',
    'depends': [
        'base',
        'account',
        'om_recurring_payments',  # Dependencia clave para la facturación recurrente
        'stock',  # Para la gestión de equipos
        'silver_contract', # Dependencia del contrato base
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/isp_contract_views.xml',
        'views/isp_equipment_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
    ],
    'application': True,
}
