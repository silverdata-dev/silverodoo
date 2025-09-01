{
    'name': 'Silverlead Customizations',
    'version': '17.0.1.0.0',
    'summary': "Añade la etapa 'Supervisor' a CRM y el campo 'ID Cliente' a los contactos.",
    'author': 'Gemini',
    'license': 'AGPL-3',
    'category': 'Sales/CRM',
    'depends': [
        'crm',  # Dependencia necesaria para modificar crm.lead
    ],
    'data': [
        'data/crm_stage_data.xml',
        'data/cron_jobs.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
}
