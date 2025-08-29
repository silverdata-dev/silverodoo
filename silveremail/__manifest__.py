{
    'name': 'Silver Email Sender',
    'version': '17.0.1.0.0',
    'summary': 'Agrega una acción para enviar plantillas de email a clientes.',
    'author': 'Gemini',
    'category': 'Customer Relationship Management',
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'wizards/send_template_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
