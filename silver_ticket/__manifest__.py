{
    'name': 'Silver Ticket',
    'version': '1.0',
    'summary': 'Módulo de Tickets para ISP',
    'description': 'Gestión de tickets de soporte para clientes de un ISP, integrado con contratos y red.',
    'author': 'Tu Nombre',
    'website': 'https://www.tuempresa.com',
    'category': 'Services/Helpdesk',
    'depends': [
        'silver_provisioning',
        'silver_network',
        'silver_contract',
        'helpdesk_mgmt',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/silver_ticket_views.xml',
        'views/contract_contract_views.xml',
    ],
    'installable': True,
    'application': True,
}
