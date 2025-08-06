from odoo import models, fields

class IspOltCardPort(models.Model):
    _name = 'isp.olt.card.port'
    _description = 'Puerto de Tarjeta OLT'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Puerto')
    num_port = fields.Integer(string='Numero Puerto')
    olt_card_id = fields.Many2one('isp.olt.card', string='Tarjeta OLT')
    capacity_port_pon = fields.Selection([], string='Total PON')
    capacity_usage_port_pon = fields.Integer(string='Usada PON', readonly=True)
    s_vlan = fields.Integer(string='s-vlan')
    c_vlan = fields.Integer(string='c-vlan')
    is_management_vlan = fields.Boolean(string='Vlan de Gestion')
    is_extra_serviceport = fields.Boolean(string='Serviport Extra')
    mgs_vlan = fields.Integer(string='gs-vlan')
    mgc_vlan = fields.Integer(string='gc-vlan')
    is_srvprofile = fields.Boolean(string='ONT Srvprofile')
    ont_srvprofile = fields.Char(string='ont-srvprofile')
    is_line_profile = fields.Boolean(string='ONT Lineprofile')
    ont_lineprofile = fields.Char(string='ont-lineprofile')
    type_access_net = fields.Selection([], string='Tipo')
    dhcp_custom_server = fields.Char(string='DHCP Leases')
    interface = fields.Char(string='Interface')
    dhcp_client = fields.Boolean(string='Profiles VSOL')
    pri_onu_standar = fields.Char(string='PRI ONU Standar:')
    pri_onu_bridge = fields.Char(string='PRI ONU Bridge:')
    is_custom_pppoe_profile = fields.Boolean(string='Custom PPPoE Profile')
    name_custom_pppoe_profile = fields.Char(string='Name Custom PPPoE Profile')
    realm_name = fields.Char(string='REALM')
    is_reverse_onuid = fields.Boolean(string='Reservar ONU IDs')
    number_reverse = fields.Integer(string='Numero')
    ip_address_line_ids = fields.One2many('isp.ip.address.line', 'port_id', string='Direcciones IP')
    ip_address_ids = fields.One2many('isp.ip.address', 'port_id', string='Direcciones IP')
    splitter1_count = fields.Integer(string='Conteo Splitter 1', compute='_compute_splitter1_count')
    splitter2_count = fields.Integer(string='Conteo Splitter 2', compute='_compute_splitter2_count')
    contracts_port_count = fields.Integer(string='Conteo Puerto Olt', compute='_compute_contracts_port_count')

    def _compute_splitter1_count(self):
        self.splitter1_count = 0

    def _compute_splitter2_count(self):
        self.splitter2_count = 0

    def _compute_contracts_port_count(self):
        self.contracts_port_count = 0

    def create_splitter_primary(self):
        pass

    def create_splitter_secondary(self):
        pass

    def active_contracts(self):
        pass
