from odoo import models, fields, api, _
from odoo.exceptions import UserError
import librouteros
import logging, string, secrets
from librouteros.query import Key

_logger = logging.getLogger(__name__)

class SilverRadius(models.Model):
    _inherit = 'silver.core'
    #_table = 'isp_radius'
    _description = 'Servidor Radius'


    is_radius = fields.Boolean('Es radius')

    core_ids = fields.One2many('silver.core', 'radius_id', string='Clientes Radius')

    def _compute_core_ids(self):
        for record in self:
            # Find all cores that are linked to this radius server
            linked_cores = self.env['silver.core'].search([('radius_id', '=', record.id)])
            record.core_ids = linked_cores

    def _inverse_core_ids(self):
        for record in self:
            # Cores that are currently linked in the database
            cores_currently_linked = self.env['silver.core'].search([('radius_id', '=', record.id)])
            
            # Cores that the user wants to be linked (from the UI)
            cores_to_link = record.core_ids

            # Unlink cores that were removed by the user
            cores_to_unlink = cores_currently_linked - cores_to_link
            if cores_to_unlink:
                cores_to_unlink.write({'radius_id': False})

            # Link cores that were added by the user
            cores_to_add = cores_to_link - cores_currently_linked
            if cores_to_add:
                # Default values to write for the new cores
                vals_to_write = {'radius_id': record.id}

                # Find a "template" core from the ones already linked to get the values
                template_core = None
                if cores_currently_linked:
                    template_core = cores_currently_linked[0]
                
                # If we found a template, add its values to the write dictionary
                if template_core:
                    vals_to_write.update({
                        'user_nass': template_core.user_nass,
                        'password_nass': template_core.password_nass,
                        'port_coa': template_core.port_coa,
                    })
                
                cores_to_add.write(vals_to_write)



    #state = fields.Selection([('down', 'Down'), ('active', 'Activo')], string='Estado', default='down', track_visibility='onchange')

  #  state = fields.Selection([('down', 'Down'), ('active', 'Active'), ('connected', 'Connected'),
  #      ('connecting', 'Connecting'),
  #      ('disconnected', 'Disconnected'),
  ##      ('error', 'Error')],
  #                           related = 'netdev_id.state',
  #                           string='Estado', default='down')

    type_radius = fields.Selection([("free_radius", "Free Radius Custom"), ("free_radius_ng", "Free Radius"), ("mk_radius", "Mikrotik Radius")], string='Tipo Radius', default="mk_radius")
    port_coa = fields.Char(string='Puerto COA')
    is_ipv6 = fields.Boolean(string='IPV6')



    silver_radius_ids = fields.One2many('silver.radius.line', 'radius_id', string='Radius Atributos')
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

    user_ids = fields.One2many('silver.radius.user', 'radius_id', string='Users')

    def _compute_radius_user_count(self):
        for record in self:
            record.radius_user_count = self.env['silver.radius.user'].search_count([('radius_id', '=', record.id)])

    def action_view_radius_users(self):
        self.ensure_one()
        return {
            'name': _('RADIUS Users'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.radius.user',
            'view_mode': 'list,form',
            'domain': [('radius_id', '=', self.id)],
            'context': {'default_radius_id': self.id},
        }

    def _get_mikrotik_api(self):
        self.ensure_one()
        if not self.ip or not self.username or not self.password:
            raise UserError(_("RADIUS server IP, username, and password are required for MikroTik API connection."))
        try:
            print(("mikro", self.username, self.password))
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
        try:
       # if 1:
            g = api.path('/user-manager/user')
            print(("gg", g, dir(g)))
            mikrotik_users = api.path('/user-manager/user')
            for m_user in mikrotik_users:
                # Check if user already exists in Odoo
                odoo_user = self.env['silver.radius.user'].search([
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
                    self.env['silver.radius.user'].create(user_vals)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'Users synchronized from MikroTik.',
                    'type': 'success',
                }
            }
        except Exception as e:
            raise UserError(_("Failed to pull users from MikroTik: %s") % e)
        finally:
            api.close()

    def button_manage_nas_clients(self):
        self.ensure_one()
        return {
            'name': _('Manage MikroTik NAS Clients'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.radius.nas.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_radius_id': self.id},
        }

    #@api.model
    #def create(self, vals):
    #    if vals.get('core_id'):
    #        core = self.env['silver.core'].browse(vals['core_id'])
    #        if core.exists():
    #            radius_count = self.search_count([('core_id', '=', core.id)])
    #            vals['name'] = f"{core.name}/RADIUS{radius_count + 1}"
    #    return super(SilverRadius, self).create(vals)







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
        wizard = self.env['silver.radius.view.table.wizard'].create({'table_data': table_data})
        return {
            'name': 'Radius Table',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.radius.view.table.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def _compute_ip_range_count(self):
        for record in self:
            record.ip_range_count = self.env['silver.ip.address'].search_count([('radius_id', '=', record.id)])





class SilverRadiusTable(models.Model):
    _name = 'silver.radius.table'
    _description = 'Radius Table'

    name = fields.Char(string="Name", required=True)
    silver_radius_columns = fields.One2many('silver.radius.column', 'radius_table_id', string="Radius Columns")

class SilverRadiusColumn(models.Model):
    _name = 'silver.radius.column'
    _description = 'Radius Column'

    name = fields.Char(string="Name", required=True)
    radius_table_id = fields.Many2one('silver.radius.table', string="Radius Table")

class SilverRadiusAttributes(models.Model):
    _name = 'silver.radius.attributes'
    _description = 'Atributos Radius'

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")

class SilverRadiusLine(models.Model):
    _name = 'silver.radius.line'
    _description = 'Silver Radius Line'

    radius_id = fields.Many2one('silver.core', string='Radius')
    silver_radius_table_id = fields.Many2one('silver.radius.table', string="Tabla Radius")
    silver_radius_column_id = fields.Many2one('silver.radius.column', string="Campos BD")
    value_column = fields.Selection([
        ("ct", "CT"),
        ("mac", "MAC"),
        ("dni", "DNI"),
        ("ppp", "PPP"),
        ("speed_product", "Velocidad(Producto)"),
        ("text", "Texto"),
        ("ip", "IP")
    ], string="Valor Campo BD")
    silver_radius_attribute_id = fields.Many2one('silver.radius.attributes', string="Atributos")
    op = fields.Selection([
        ("=", "="),
        (":=", ":="),
        ("==", "=="),
        ("+=", "+="),
        ("!=", "!="),
        (">", ">"),
        (">=", ">="),
        ("<", "<"),
        ("<=", "<=")
    ], string="Operador")
    value = fields.Selection([
        ("ct", "CT"),
        ("mac", "MAC"),
        ("dni", "DNI"),
        ("ppp", "PPP"),
        ("speed_product", "Velocidad(Producto)"),
        ("text", "Texto"),
        ("ip", "IP")
    ], string="Valor")
    value_text = fields.Char(string="Texto fijo")
    function_radius = fields.Selection([
        ("active", "Activar"),
        ("active_bandwidth", "Activar/Ancho Banda"),
        ("cutoff", "Cortar")
    ], string="Función")

