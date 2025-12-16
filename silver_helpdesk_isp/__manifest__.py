{
    'name': 'Silver Helpdesk - ISP/Network Integration',
    'version': '19.0.1.0.0',
    'summary': 'Integration between Helpdesk and Network/ISP modules',
    'category': 'Services/Helpdesk',
    'depends': [
        'silver_helpdesk_contract',
        'silver_network',
        'silver_provisioning',
    ],
    'data': [
        'views/helpdesk_ticket_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
