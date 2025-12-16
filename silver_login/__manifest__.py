# -*- coding: utf-8 -*-
{
    'name': 'Silver Login - Autenticación RADIUS',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'summary': 'Autentica usuarios de Odoo contra un servidor RADIUS.',
    'description': """
Este módulo permite a Odoo usar un servidor RADIUS para la autenticación de usuarios.
Está diseñado para integrarse con entornos de red donde servicios como los routers MikroTik
también se autentican contra el mismo servidor RADIUS.

Características:
- Inicio de sesión de usuarios basado en RADIUS.
- Configuración del servidor RADIUS desde los ajustes de Odoo.
- Creación automática de usuarios en Odoo en el primer inicio de sesión exitoso.
- Guarda las credenciales en la sesión del usuario para uso externo (ej. API de MikroTik).

Dependencias Externas:
- pyrad
    """,
    'author': 'SilverData',
    'website': 'https://www.silverdata.org',
    'category': 'Tools',
    'depends': ['base', 'web', 'silver_base'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'external_dependencies': {
        'python': ['pyrad'],
    },
}
