{
    'name': 'Silver Helpdesk - ISP/Network Integration',
    'version': '17.0.1.0.0',
    'summary': 'Integration between Helpdesk and Network/ISP modules',
    'category': 'Services/Helpdesk',
    'depends': [
        'silver_helpdesk_contract',
        'silver_network',
    ],
    'data': [
        'views/helpdesk_ticket_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
