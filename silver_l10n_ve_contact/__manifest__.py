# -*- coding: utf-8 -*-
{
    'name': "Silver Odoo - Venezuela Localization Contact",
    'summary': """
        Integrates Venezuelan contact fields into Silver Odoo's contact views.
    """,
    'author': "Silverdata",
    'website': "https://www.silverdata.com",
    'category': 'Localization',
    'version': '17.0.1.0.0',
    'depends': [
        'silver_crm',
        'l10n_ve_contact',
        'silver_l10n_ve_base'
    ],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
