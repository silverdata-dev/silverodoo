{
    'name': 'Silver Helpdesk - Stock Integration',
    'version': '17.0.1.0.0',
    'summary': 'Integration between Helpdesk and Stock',
    'category': 'Services/Helpdesk',
    'depends': [
        'silver_helpdesk_contract',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/helpdesk_ticket_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
