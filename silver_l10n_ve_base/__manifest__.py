# -*- coding: utf-8 -*-
{
    'name': "Silver Odoo - Venezuela Localization Base",
    'summary': """
        Base module for the Venezuelan localization of Silver Odoo.
    """,
    'author': "Silverdata",
    'website': "https://www.silverdata.com",
    'category': 'Localization',
    'version': '17.0.1.0.0',
    'depends': [
        'base_vat',
        'silver_base',
        'l10n_ve_base',
        'l10n_ve_location',
    ],
    'data': [
        'data/res_country_city_data.xml',
        # 'security/ir.model.access.csv',
        'views/res_partner_address_views.xml',
        'views/silver_address_views.xml',
        'views/res_country_municipality_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
