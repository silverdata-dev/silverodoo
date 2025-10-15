# -*- coding: utf-8 -*-
{
    'name': "Silver Odoo - Collections",
    'summary': """
        API-agnostic payment collection and reconciliation for contracts.
    """,
    'author': "Silverdata",
    'website': "https://www.silverdata.com",
    'category': 'Accounting/Payment',
    'version': '17.0.1.0.0',
    'depends': [
        'silver_contract',
        'silver_accounting',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/payment_provider_data.xml',
        'views/payment_provider_views.xml',
        'views/payment_transaction_views.xml',
        'views/silver_contract_views.xml',
    ],
    'installable': True,
    'application': True,
}
