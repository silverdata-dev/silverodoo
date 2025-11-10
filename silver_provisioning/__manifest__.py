{
    'name': 'Silver Provisioning',
    'version': '17.0.1.0.0',
    'summary': 'Bridge module for ISP and Contract functionalities',
    'description': 'This module contains all the logic that connects silver_contract with silver_isp, allowing for provisioning.',
    'author': 'Gemini',
    'website': 'https://www.gemini.com',
    'category': 'Services/Telecommunications',
    'depends': ['web', 'silver_network', 'silver_contract', 'silver_base', 'silver_product', 'stock'],
    'data': [
# 'views/assets.xml',

        'security/ir.model.access.csv',
        'views/silver_olt_discovered_onu_views.xml',
        'wizards/provisioning_wizard_views.xml',
        'wizards/select_discovered_onu_views.xml',
        'views/silver_display_info_wizard_views.xml',
        'views/silver_contract_views.xml',
        'views/silver_cutoff_date_views.xml',
        'views/silver_ap_views.xml',

        'views/silver_box_views.xml',
        'views/silver_splitter_views.xml',
        'views/silver_olt_views.xml',
        #'views/silver_olt_card_views.xml',
        'views/silver_olt_card_port_views.xml',

        #'views/templates.xml',
    # only loaded in demonstration mode
        'views/silver_core_views.xml',
        'views/silver_node_views.xml',
        'views/silver_ip_address_views.xml',


    ],
    'installable': True,
    'application': False,
}
