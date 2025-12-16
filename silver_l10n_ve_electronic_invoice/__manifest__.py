# -*- coding: utf-8 -*-
{
    'name': "Silver Odoo - Venezuela Localization Electronic Invoice",
    'summary': """
        API-agnostic electronic invoicing for Venezuela.
    """,
    'author': "Silverdata",
    'website': "https://www.silverdata.com",
    'category': 'Localization',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'silver_l10n_ve_accounting',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/res_company_views.xml',
    ],
    'installable': True,
    'application': True,
}
