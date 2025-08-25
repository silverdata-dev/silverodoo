from odoo import models, fields, api, _
from odoo.exceptions import UserError
import librouteros

class IspRadius(models.Model):
    _name = 'isp.radius'
    _description = 'Servidor Radius'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    _inherits = {
                 'isp.netdev':'netdev_id'}


    netdev_id = fields.Many2one('isp.netdev', required=True, ondelete="cascade")


    name = fields.Char(string='Hostname', required=True, readonly=True, copy=False, default='New')
    ip_core_radius = fields.Char(string='IP Core Radius')
    port_core_radius = fields.Char(string='Puerto Core Radius')
    user_core_radius = fields.Char(string='Usuario Core Radius')
    password_core_radius = fields.Char(string='Password Core Radius')
    database = fields.Char(string='Database')
    core_id = fields.Many2one('isp.core', string='Equipo Core', readonly=False, required=False, ondelete='cascade')
    type_radius = fields.Selection([], string='Tipo Radius')
    port_coa = fields.Char(string='Puerto COA')
    is_ipv6 = fields.Boolean(string='IPV6')

    isp_radius_ids = fields.One2many('isp.radius.line', 'radius_id', string='Radius Atributos')
    type_table = fields.Selection([], string='Tipo Tabla')
    is_cutoff = fields.Boolean(string='Corte')
    is_realm_port = fields.Boolean(string='Realm Port')
    is_user_profile = fields.Boolean(string='User Profile')
    is_extract_ip_rd = fields.Boolean(string='Extraer IP RD')
    is_pppoe = fields.Boolean(string='PPPoE')
    is_ipoe = fields.Boolean(string='IPoE')
    radius_domain = fields.Boolean(string='Dominio Radius')
    domain_text = fields.Char(string='Texto Dominio')
    general_key = fields.Boolean(string='Clave General')
    general_key_text = fields.Char(string='Texto Clave General')
    profile_active = fields.Char(string='Perfil Activo')
    profile_cut = fields.Char(string='Perfil Cortado')
    profile_suspended = fields.Char(string='Perfil Suspendido')
    code_mac = fields.Selection([], string='Codigo MAC')
    default_control = fields.Boolean(string='Control por Defecto')
    perfil_control = fields.Boolean(string='Control por Perfil')
    ip_range_count = fields.Integer(string='IP Ranges', compute='_compute_ip_range_count')
    radius_user_count = fields.Integer(string='RADIUS Users', compute='_compute_radius_user_count')

    nas_address = fields.Char(string='NAS Address')
    nas_secret = fields.Char(string='NAS Secret')

    def _compute_radius_user_count(self):
        for record in self:
            record.radius_user_count = self.env['isp.radius.user'].search_count([('radius_id', '=', record.id)])

    def action_view_radius_users(self):
        self.ensure_one()
        return {
            'name': _('RADIUS Users'),
            'type': 'ir.actions.act_window',
            'res_model': 'isp.radius.user',
            'view_mode': 'tree,form',
            'domain': [('radius_id', '=', self.id)],
            'context': {'default_radius_id': self.id},
        }

    def _get_mikrotik_api(self):
        self.ensure_one()
        if not self.ip or not self.username or not self.password:
            raise UserError(_("RADIUS server IP, username, and password are required for MikroTik API connection."))
        try:
            api = librouteros.connect(
                username=self.username,
                password=self.password,
                host=self.ip,
                port=int(self.port),
                encoding='latin-1'
            )
            return api
        except Exception as e:
            raise UserError(_("Failed to connect to MikroTik API: %s") % e)

    def action_pull_users_from_mikrotik(self):
        self.ensure_one()
        api = self._get_mikrotik_api()
       # try:
        if 1:
            g = api.path('/user-manager/user')
            print(("gg", g, dir(g)))
            mikrotik_users = api.path('/user-manager/user')
            for m_user in mikrotik_users:
                # Check if user already exists in Odoo
                odoo_user = self.env['isp.radius.user'].search([
                    ('radius_id', '=', self.id),
                    ('username', '=', m_user['name'])
                ], limit=1)

                user_vals = {
                    'radius_id': self.id,
                    'username': m_user['name'],
                    'password': m_user.get('password', ''), # Passwords are not usually readable via API
                    'profile': m_user.get('profile', ''),
                    'comment': m_user.get('comment', ''),
                    'disabled': m_user.get('disabled', 'no') == 'yes',
                }

                if odoo_user:
                    odoo_user.write(user_vals)
                else:
                    self.env['isp.radius.user'].create(user_vals)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'Users synchronized from MikroTik.',
                    'type': 'success',
                }
            }
        #except Exception as e:
        #    raise UserError(_("Failed to pull users from MikroTik: %s") % e)
        #finally:
        #    api.close()

    def button_manage_nas_clients(self):
        self.ensure_one()
        return {
            'name': _('Manage MikroTik NAS Clients'),
            'type': 'ir.actions.act_window',
            'res_model': 'isp.radius.nas.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_radius_id': self.id},
        }

    @api.model
    def create(self, vals):
        if vals.get('core_id'):
            core = self.env['isp.core'].browse(vals['core_id'])
            if core.exists():
                radius_count = self.search_count([('core_id', '=', core.id)])
                vals['name'] = f"{core.name}/RADIUS{radius_count + 1}"
        return super(IspRadius, self).create(vals)

    def write(self, vals):
        if 'core_id' in vals:
            new_core = self.env['isp.core'].browse(vals['core_id'])
            if new_core.exists():
                for record in self:
                    radius_count = self.search_count([('core_id', '=', new_core.id)])
                    record.name = f"{new_core.name}/RADIUS{radius_count + 1}"
        return super(IspRadius, self).write(vals)

    def action_connect_radius(self):
        self.ensure_one()
        # Simulate connection test
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Connection Test',
                'message': 'Connection to Radius server was successful!',
                'type': 'success',
            }
        }

    def action_view_table(self):
        self.ensure_one()
        # Simulate fetching table data
        table_data = "This is a placeholder for the table data."
        wizard = self.env['isp.radius.view.table.wizard'].create({'table_data': table_data})
        return {
            'name': 'Radius Table',
            'type': 'ir.actions.act_window',
            'res_model': 'isp.radius.view.table.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def _compute_ip_range_count(self):
        for record in self:
            record.ip_range_count = self.env['isp.ip.address'].search_count([('radius_id', '=', record.id)])



    def button_test_connection(self):
        print(("netdev", self.netdev_id, self.name))
        return self.netdev_id.button_test_connection()


    def button_get_system_info(self):
        return self.netdev_id.button_get_system_info()

    def button_view_interfaces(self):
        return self.netdev_id.button_view_interfaces()

    def button_view_routes(self):
        return self.netdev_id.button_view_routes()

    def button_view_ppp_active(self):
        return self.netdev_id.button_view_ppp_active()
    def button_view_firewall_rules(self):
        return self.netdev_id.button_view_firewall_rules()
    def button_view_queues(self):
        return self.netdev_id.button_view_queues()

    def button_add_update_radius_client(self):
        return self.netdev_id.button_add_update_radius_client()


    def button_remove_radius_client(self):
        return self.netdev_id.button_remove_radius_client()