# -*- coding: utf-8 -*-
import logging
import socket
import io

from odoo import api, models, exceptions, SUPERUSER_ID
from odoo.http import request

_logger = logging.getLogger(__name__)

try:
    from pyrad.client import Client
    from pyrad.dictionary import Dictionary
    from pyrad.packet import AccessAccept, AccessRequest
    PYRAD_AVAILABLE = True
except ImportError:
    PYRAD_AVAILABLE = False
    _logger.warning("The 'pyrad' library is not installed. RADIUS authentication will be disabled.")

class ResUsers(models.Model):
    _inherit = 'res.users'

    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        # For safety, the admin user should always use the standard Odoo authentication
        if login == 'admin':
            return super(ResUsers, cls)._login(db, login, password, user_agent_env)

        try:
            # First, try to authenticate using the standard Odoo method.
            return super(ResUsers, cls)._login(db, login, password, user_agent_env)
        except exceptions.AccessDenied:
            # If standard authentication fails, proceed with RADIUS as a fallback.
            _logger.info(f"Standard Odoo login failed for user '{login}'. Attempting RADIUS authentication.")

            # Use a new cursor and environment, as the previous transaction might be aborted.
            with cls.pool.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                config = env['ir.config_parameter'].sudo()
                
                radius_enabled = config.get_param('silver_login.radius_auth_enabled')
                if not PYRAD_AVAILABLE or not radius_enabled:
                    # If RADIUS is not configured, re-raise the original AccessDenied exception.
                    raise

                # RADIUS authentication logic
                radius_ip = config.get_param('silver_login.radius_server_ip')
                radius_port = int(config.get_param('silver_login.radius_server_port', 1812))
                radius_secret = config.get_param('silver_login.radius_server_secret')

                if not all([radius_ip, radius_port, radius_secret]):
                    _logger.error("RADIUS authentication is enabled but server details are not fully configured.")
                    # Re-raise to indicate a system config error, not a user password error.
                    raise exceptions.AccessDenied("Error en la configuración del sistema de autenticación.")

                # Create a minimal RADIUS dictionary in memory
                mem_dict = io.StringIO("""
                ATTRIBUTE    User-Name              1   string
                ATTRIBUTE    User-Password          2   string
                """)

                server = Client(
                    server=radius_ip,
                    authport=radius_port,
                    secret=radius_secret.encode('utf-8'),
                    dict=Dictionary(mem_dict)
                )
                
                req = server.CreateAuthPacket(code=AccessRequest, User_Name=login)
                req["User-Password"] = req.PwCrypt(password)

                try:
                    reply = server.SendPacket(req)
                except socket.timeout:
                    _logger.error(f"RADIUS server {radius_ip} timed out.")
                    raise exceptions.AccessDenied("El servicio de autenticación no está disponible.")
                except Exception as e:
                    _logger.error(f"An unexpected error occurred while contacting the RADIUS server: {e}")
                    raise exceptions.AccessDenied("Ocurrió un error inesperado durante la autenticación.")

                if reply.code == AccessAccept:
                    _logger.info(f"RADIUS authentication successful for user: {login}")
                    
                    # Find or create the user in Odoo
                    user = env['res.users'].search([('login', '=', login)])
                    if not user:
                        auto_create = config.get_param('silver_login.radius_auto_create_users')
                        if auto_create:
                            _logger.info(f"User {login} not found in Odoo. Creating new user.")
                            new_user = env['res.users'].create({
                                'name': login,
                                'login': login,
                                'password': 'RADIUS_USER_NO_PASSWORD', # Set a placeholder
                                'active': True,
                            })
                            user_id = new_user.id
                        else:
                            _logger.warning(f"RADIUS user {login} is not an Odoo user and auto-creation is disabled.")
                            raise exceptions.AccessDenied()
                    else:
                        user_id = user.id

                    # Store credentials in the session for MikroTik or other services
                    if request:
                        request.session['radius_user'] = login
                        request.session['radius_password'] = password
                        _logger.debug(f"Stored RADIUS credentials for {login} in the current session.")

                    return user_id
                else:
                    _logger.warning(f"RADIUS authentication failed for user: {login}")
                    # This is the final failure point, raise the definitive AccessDenied.
                    raise exceptions.AccessDenied()

    def _check_credentials(self, password, env):
        # Check if RADIUS is enabled. If so, this method will be bypassed by _login.
        # If not, or if called directly, we need to ensure it still works.
        radius_enabled = self.env['ir.config_parameter'].sudo().get_param('silver_login.radius_auth_enabled')
        
        # If RADIUS is enabled, the password stored in Odoo is likely a placeholder.
        # The actual authentication happens in _login. We can deny direct password checks here.
        if radius_enabled and self.password and 'RADIUS_USER_NO_PASSWORD' in self.password:
             raise exceptions.AccessDenied("Password authentication is disabled for this user.")
        
        # Fallback to standard credential check
        return super(ResUsers, self)._check_credentials(password, env)
