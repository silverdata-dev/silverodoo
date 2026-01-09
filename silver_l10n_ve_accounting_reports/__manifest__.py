{
    'name': 'Silver VE - Reportes Contables (Excel)',
    'version': '19.0.1.0.0',
    'summary': 'Personalizaciones de reportes contables y fiscales a formato XLSX.',
    'author': 'SilverData',
    'website': 'https://www.silver-data.net',
    'license': 'AGPL-3',
    'category': 'Accounting/Localizations',
    'depends': [
        'accounting_pdf_reports', # Dependemos del módulo que provee los wizards
        'report_xlsx', # Dependencia clave para generar Excel
    ],
    'data': [
        # 'reports/report_sales_book_xlsx.xml', # Se añadirá más adelante
        # 'wizards/accounting_reports_views.xml', # Para añadir el botón
    ],
    'application': False,
}
