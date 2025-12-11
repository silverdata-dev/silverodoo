{
    'name': 'Silver Ticket',
    'version': '1.0',
    'summary': 'Módulo de Tickets para ISP',
    'description': 'Gestión de tickets de soporte para clientes de un ISP, integrado con contratos y red. Incluye motor de flujos de trabajo (Workflows).',
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
        'views/workflow_views.xml',
        'data/ticket_type_data.xml',
    ],
    'installable': True,
    'application': True,
}