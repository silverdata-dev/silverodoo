{
    'name': 'Silver VE - Formatos de Documentos',
    'version': '19.0.1.0.0',
    'summary': 'Personalizaciones de los formatos de Facturas, Notas de Entrega y Retenciones para Venezuela.',
    'author': 'Tu Nombre/Empresa',
    'website': 'https://www.silver-data.net',
    'license': 'AGPL-3',
    'category': 'Accounting/Localizations',
    'depends': [
        'l10n_ve_invoice',
        'l10n_ve_stock_account',
        'l10n_ve_payment_extension',
    ],
    'data': [
        'reports/report_invoice_document.xml',
        # 'reports/report_delivery_guide.xml', # Descomentar cuando se cree
        # 'reports/report_retention_voucher.xml', # Descomentar cuando se cree
    ],
    'application': False,
}
