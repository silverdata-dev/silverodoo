{
    'name': 'Silver Product',
    'version': '17.0.1.0.0',
    'summary': 'Customizations for product views',
    'author': 'SilverData',
    'website': 'https://www.silverdata.org',
    'category': 'Sales',
    'depends': ['product'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_view.xml',
    ],
    'installable': True,
    'application': False,
}
