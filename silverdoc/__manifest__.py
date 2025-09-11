{
    'name': 'SilverDoc - Documentación de Proyectos',
    'version': '17.0.1.0.0',
    'summary': 'Módulo para la gestión jerárquica de documentación de proyectos.',
    'author': 'Gemini',
    'website': 'https://github.com/gemini',
    'category': 'Project',
    'depends': [
        'base',
        'project',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/silverdoc_project_views.xml',
        'views/silverdoc_module_views.xml',
        'views/silverdoc_topic_views.xml',
        'views/silverdoc_document_views.xml',
        'views/silverdoc_menus.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
