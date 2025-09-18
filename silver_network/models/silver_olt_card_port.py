from odoo import models, fields, api

class SilverOltCardPort(models.Model):
    _name = 'silver.olt.card.port'
    _description = 'Puerto de Tarjeta OLT'
    #_table = 'isp_olt_card_port'
    _inherit = [ 'mail.thread', 'mail.activity.mixin']

    _inherits = { 'silver.netdev': 'netdev_id'}


    name = fields.Char(string='Nombre')

    netdev_id = fields.Many2one('silver.netdev', required=True, ondelete="cascade")


    num_port = fields.Integer(string='Numero Puerto')
    olt_id = fields.Many2one('silver.olt', string='Equipo OLT', required=False, ondelete='cascade')
    olt_card_n = fields.Integer(string='Tarjeta', required=False, default=0)
    olt_card_id = fields.Many2one('silver.olt.card', string='Tarjeta OLT', required=False, ondelete='cascade')
    capacity_port_pon = fields.Selection([("32","32"), ("64", "64"), ("128", "128"), ("256","256")], string='Total PON')
    capacity_usage_port_pon = fields.Integer(string='Usada PON', readonly=False)
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
    type_access_net = fields.Selection(
        [('inactive', 'Inactivo'), ('dhcp', 'DHCP Leases'), ('manual', 'IP Asignada manualmente'),
         ('system', 'IP Asignada por el sistema')], default='inactive', string='Tipo Acceso', required=True, related='netdev_id.type_access_net',)

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
   # splitter1_count = fields.Integer(string='Conteo Splitter 1', compute='_compute_splitter1_count')
   # splitter2_count = fields.Integer(string='Conteo Splitter 2', compute='_compute_splitter2_count')
   # contracts_port_count = fields.Integer(string='Conteo Puerto Olt', compute='_compute_contracts_port_count')


    netdev_type = fields.Selection(
        related='netdev_id.netdev_type',
        default='port',
        store=True,
        readonly=False
    )

    def _compute_splitter1_count(self):
        for record in self:
            record.splitter1_count = self.env['silver.splitter'].search_count([('olt_port_id', '=', record.id), ('type_splitter', '=', '1')])

    def _compute_splitter2_count(self):
        for record in self:
            record.splitter2_count = self.env['silver.splitter'].search_count([('olt_port_id', '=', record.id), ('type_splitter', '=', '2')])

    def _compute_contracts_port_count(self):
        for record in self:
            record.contracts_port_count = self.env['silver.contract'].search_count([('olt_port_id', '=', record.id)])

    def create_splitter_primary(self):
        self.ensure_one()
        new_splitter = self.env['silver.splitter'].create({

#            'name': f"Splitter Primary for {self.name}",
#            'olt_port_id': self.id,

            'olt_card_port_id': self.id,
            'type_splitter': '1',
        })
        return {
            'name': 'Splitter Primario Creado',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.splitter',
            'view_mode': 'form',
            'res_id': new_splitter.id,
            'target': 'current',
        }

    def create_splitter_secondary(self):
        self.ensure_one()
        new_splitter = self.env['silver.splitter'].create({

#            'name': f"Splitter Secondary for {self.name}",
#            'olt_port_id': self.id,

            'olt_card_port_id': self.id,
            'type_splitter': '2',
        })
        return {
            'name': 'Splitter Secundario Creado',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.splitter',
            'view_mode': 'form',
            'res_id': new_splitter.id,
            'target': 'current',
        }

    def active_contracts(self):
        self.ensure_one()
        # Simulate activating contracts
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Activate Contracts',
                'message': 'Contracts activated successfully!',
                'type': 'success',
            }
        }

    def action_view_splitter1(self):
        self.ensure_one()
        return {
            'name': 'Splitter Primario',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.splitter',
            'view_mode': 'tree,form',
            'domain': [('olt_card_port_id', '=', self.id), ('type_splitter', '=', '1')],
            'context': {'default_olt_card_port_id': self.id, 'default_type_splitter': '1'},
            'target': 'current',
        }

    def action_view_splitter2(self):
        self.ensure_one()
        return {
            'name': 'Splitter Secundario',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.splitter',
            'view_mode': 'tree,form',
            'domain': [('olt_card_port_id', '=', self.id), ('type_splitter', '=', '2')],
            'context': {'default_olt_card_port_id': self.id, 'default_type_splitter': '2'},
            'target': 'current',
        }

    def action_view_contracts(self):
        self.ensure_one()
        return {
            'name': 'Contratos',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.contract',
            'view_mode': 'tree,form',
            'domain': [('olt_card_port_id', '=', self.id)],
            'context': {'default_olt_card_port_id': self.id},
            'target': 'current',
        }
