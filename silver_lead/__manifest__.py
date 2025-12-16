{
    'name': 'Silverlead Customizations',
    'version': '19.0.1.0.1',
    'summary': 'Manejo de leads desde excel, con vendedores, zonas y seguimiento de instalación.',
    'author': 'Gemini & Sergio',
    'license': 'AGPL-3',
    'category': 'Sales/CRM',
    'depends': [
        'crm',
        'silver_base',
        'silver_crm',
        'silver_network',
        'silver_contract',
        'silver_provisioning',

    ],
    'data': [
        'security/ir.model.access.csv',
        'data/crm_stage_data.xml',
        'data/cron_jobs.xml',
        'views/res_partner_views.xml',
        'views/crm_lead_views.xml',
        'views/silverlead_zona_views.xml',
    ],
    'installable': True,
    'application': True,
}
