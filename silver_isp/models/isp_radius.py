from odoo import models, fields

class IspRadius(models.Model):
    _name = 'isp.radius'
    _description = 'Servidor Radius'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Hostname', required=True)
    ip_core_radius = fields.Char(string='IP Core Radius')
    port_core_radius = fields.Char(string='Puerto Core Radius')
    user_core_radius = fields.Char(string='Usuario Core Radius')
    password_core_radius = fields.Char(string='Password Core Radius')
    database = fields.Char(string='Database')
    core_id = fields.Many2one('isp.core', string='Equipo Core', readonly=True)
    type_radius = fields.Selection([], string='Tipo Radius')
    ip_server = fields.Char(string='IP Servidor')
    port_server = fields.Char(string='Puerto Servidor')
    port_coa = fields.Char(string='Puerto COA')
    username_server = fields.Char(string='Usuario Servidor')
    password_server = fields.Char(string='Password Servidor')
    is_ipv6 = fields.Boolean(string='IPV6')
    type_access_net = fields.Selection([], string='Tipo Acceso')
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
    ip_address_line_ids = fields.One2many('isp.ip.address.line', 'radius_id', string='Direcciones IP')
    ip_address_ids = fields.One2many('isp.ip.address', 'radius_id', string='Direcciones IP')
    state = fields.Selection([('down', 'Down'), ('active', 'Active')], string='Estado', default='down')

    def action_connect_radius(self):
        pass

    def action_view_table(self):
        pass
