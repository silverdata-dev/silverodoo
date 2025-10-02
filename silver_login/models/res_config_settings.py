# -*- coding: utf-8 -*-
import logging
import socket
import io
from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from pyrad.client import Client
    from pyrad.dictionary import Dictionary
    from pyrad.packet import AccessAccept, AccessRequest
    PYRAD_AVAILABLE = True
except ImportError:
    PYRAD_AVAILABLE = False
    _logger.warning("La librería 'pyrad' no está instalada. La autenticación RADIUS no funcionará.")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    radius_auth_enabled = fields.Boolean(
        string='Activar Autenticación RADIUS',
        config_parameter='silver_login.radius_auth_enabled'
    )
    radius_server_ip = fields.Char(
        string='IP del Servidor RADIUS',
        config_parameter='silver_login.radius_server_ip'
    )
    radius_server_port = fields.Integer(
        string='Puerto del Servidor RADIUS',
        default=1812,
        config_parameter='silver_login.radius_server_port'
    )
    radius_server_secret = fields.Char(
        string='Secreto del Servidor RADIUS',
        config_parameter='silver_login.radius_server_secret'
    )
    radius_auto_create_users = fields.Boolean(
        string='Crear Usuarios de Odoo Automáticamente',
        default=True,
        help="Si está marcado, se creará un nuevo usuario de Odoo si la autenticación RADIUS es exitosa para un usuario nuevo.",
        config_parameter='silver_login.radius_auto_create_users'
    )
    # Campos para el test de conexión
    radius_test_user = fields.Char(
        string='Usuario de Prueba',
        config_parameter='silver_login.radius_test_user'
    )
    radius_test_password = fields.Char(
        string='Contraseña de Prueba',
        password=True,
        config_parameter='silver_login.radius_test_password'
    )

    def test_radius_connection(self):
        """
        Método para probar la conexión con el servidor RADIUS.
        Devuelve una notificación en lugar de un UserError para ser compatible
        con el ciclo de guardado/recarga de la vista de ajustes.
        """
        print("a0")
        if not PYRAD_AVAILABLE:
            return self._show_notification('danger', "La librería 'pyrad' no está instalada. Por favor, instálala (`pip install pyrad`).")

        print("a1")
        if not self.radius_server_ip or not self.radius_server_secret or not self.radius_test_user or not self.radius_test_password:
            return self._show_notification('warning', "Por favor, completa la IP del servidor, el secreto, el usuario y la contraseña de prueba.")

        # Crear un diccionario RADIUS mínimo en memoria
        mem_dict = io.StringIO("""
        ATTRIBUTE    User-Name              1   string
        ATTRIBUTE    User-Password          2   string
        ATTRIBUTE    Reply-Message          18  string
        """)

        print("a2")
        server = Client(
            server=self.radius_server_ip,
            authport=self.radius_server_port,
            secret=self.radius_server_secret.encode('utf-8'),
            dict=Dictionary(mem_dict)
        )
        
        print("a3")
        req = server.CreateAuthPacket(code=AccessRequest, User_Name=self.radius_test_user)
        req["User-Password"] = req.PwCrypt(self.radius_test_password)

        #try:
        reply = server.SendPacket(req)
        try:
            pass
        except socket.timeout:
            return self._show_notification('danger', f"Tiempo de espera agotado al conectar con el servidor RADIUS en {self.radius_server_ip}.")
        except Exception as e:
            _logger.error(f"Error inesperado al contactar al servidor RADIUS: {e}")
            return self._show_notification('danger', f"Ocurrió un error inesperado: {e}")

        print("a4")
        if reply.code == AccessAccept:
            return self._show_notification('success', "¡Conexión exitosa! El servidor RADIUS ha autenticado las credenciales de prueba correctamente.")
        else:
            error_message = f"Falló la autenticación. El servidor RADIUS respondió con el código: {reply.code}."
            print(("a5", reply))
            if 'Reply-Message' in reply:
                try:
                    error_message += f" Mensaje: {reply}"
                except (UnicodeDecodeError, IndexError):
                    pass  # Ignorar si el mensaje no se puede decodificar
            return self._show_notification('warning', error_message)

    def _show_notification(self, type, message):
        """Helper para mostrar notificaciones en la interfaz."""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Prueba de Conexión RADIUS',
                'message': message,
                'type': type,  # 'success', 'warning', 'danger'
                'sticky': True,
            }
        }

