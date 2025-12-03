{
    'name': 'Silver Helpdesk - Contract Integration',
    'version': '17.0.1.0.0',
    'summary': 'Integration between Helpdesk and Contracts',
    'category': 'Services/Helpdesk',
    'depends': [
        'silver_helpdesk',
        'silver_contract',
    ],
    'data': [
        'views/helpdesk_ticket_views.xml',
        'views/contract_contract_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
