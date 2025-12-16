{
    'name': 'Silver Helpdesk - Venezuela Localization',
    'version': '19.0.1.0.0',
    'summary': 'Venezuela Localization for Helpdesk',
    'category': 'Services/Helpdesk',
    'depends': [
        'silver_helpdesk_contract',
        'silver_helpdesk_isp', # For geo fields
        'silver_l10n_ve_base',
    ],
    'data': [
        'views/helpdesk_ticket_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
