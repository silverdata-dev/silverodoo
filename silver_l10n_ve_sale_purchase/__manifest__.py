# -*- coding: utf-8 -*-
{
    'name': "Silver Odoo - Venezuela Localization Sale & Purchase",
    'summary': """
        Integrates Venezuelan fiscal fields into Silver Odoo's sale and purchase flows.
    """,
    'author': "Silverdata",
    'website': "https://www.silverdata.com",
    'category': 'Localization',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'silver_contract',
        'purchase',
        'l10n_ve_sale',
        'l10n_ve_purchase',
        'silver_l10n_ve_base'
    ],
    'data': [
        # 'views/sale_order_views.xml',
        # 'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
