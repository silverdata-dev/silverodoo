# -*- coding: utf-8 -*-
{
    'name': "Silver Odoo - Venezuela Localization Accounting",
    'summary': """
        Integrates Venezuelan accounting features (invoice control numbers, IGTF, etc.)
        with Silver Odoo's accounting module.
    """,
    'author': "Silverdata",
    'website': "https://www.silverdata.com",
    'category': 'Localization',
    'version': '17.0.1.0.0',
    'depends': [
        'silver_accounting',
        'l10n_ve_invoice',
        'l10n_ve_igtf',
        'silver_l10n_ve_base'
    ],
    'data': [
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
