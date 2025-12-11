{
    'name': 'Silver Helpdesk (Base)',
    'version': '17.0.1.0.0',
'icon': 'static/description/icon.png',
    'summary': 'Módulo Base de Tickets para ISP (Workflow)',
    'description': """
        Módulo base para la gestión de tickets.
        Incluye el motor de flujos de trabajo (Workflow) y configuraciones base.
    """,
    'author': 'Gemini',
    'category': 'Services/Helpdesk',
    'depends': [
        'helpdesk_mgmt',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/helpdesk_ticket_views.xml',
        'views/workflow_views.xml',
        'data/ticket_type_data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
