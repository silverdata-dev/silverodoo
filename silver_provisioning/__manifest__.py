{
    'name': 'Silver Provisioning',
    'version': '19.0.1.0.0',
    'summary': 'Bridge module for ISP and Contract functionalities',
    'description': 'This module contains all the logic that connects silver_contract with silver_isp, allowing for provisioning.',
    'author': 'SilverData',
    'website': 'https://www.silver-data.net',
    'category': 'Services/Telecommunications',
    'depends': ['web', 'silver_network', 'silver_contract', 'silver_base', 'silver_product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/silver_linktype_data.xml',
        'views/silver_linktype_views.xml',
        'views/silver_olt_discovered_onu_views.xml',
        'wizards/provisioning_wizard_views.xml',
        'wizards/select_discovered_onu_views.xml',
        'wizards/contract_traffic_wizard_views.xml',
        'views/silver_display_info_wizard_views.xml',
        'views/silver_contract_views.xml',
        'views/silver_cutoff_date_views.xml',
        'views/silver_ap_views.xml',
            'views/silver_product.xml',

        'views/silver_box_views.xml',
        'views/silver_splitter_views.xml',
        'views/silver_olt_views.xml',
        #'views/silver_olt_card_views.xml',
        'views/silver_olt_card_port_views.xml',
        'views/silver_vlan.xml',

        #'views/templates.xml',
    # only loaded in demonstration mode
        'views/silver_core_views.xml',
        'views/silver_node_views.xml',
        'views/silver_ip_address_views.xml',

        'data/silver_contract_cron.xml',

    ],

    'assets': {
        'web.assets_backend': [
          'silver_provisioning/static/src/xml/contract_olt_status_widget.xml',
            'silver_provisioning/static/src/css/cosas.css',
            'silver_provisioning/static/src/js/contract_olt_status_widget.js',
        ],
##        'web.assets_qweb': [

    },
    'installable': True,
    'application': False,
}
