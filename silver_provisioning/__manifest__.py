{
    'name': 'Silver Provisioning',
    'version': '17.0.1.0.0',
    'summary': 'Bridge module for ISP and Contract functionalities',
    'description': 'This module contains all the logic that connects silver_contract with silver_isp, allowing for provisioning.',
    'author': 'Gemini',
    'website': 'https://www.gemini.com',
    'category': 'Services/Telecommunications',
    'depends': ['silver_network', 'silver_contract'],
    'data': [
        'views/contract_views.xml',
    ],
    'installable': True,
    'application': False,
}
