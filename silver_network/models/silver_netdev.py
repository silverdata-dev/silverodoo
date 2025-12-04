from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request
from ..models.olt_connection import OLTConnection

import logging

_logger = logging.getLogger(__name__)


def _format_speed(bits_per_second):
    bits_per_second = int(bits_per_second)
    if bits_per_second < 1000:
        return f"{bits_per_second} B/s"
    elif bits_per_second < 1000000:
        return f"{bits_per_second / 1000:.2f} KB/s"
    elif bits_per_second < 1000000000:
        return f"{bits_per_second / 1000000:.2f} MB/s"
    else:
        return f"{bits_per_second / 1000000000:.2f} GB/s"

class SilverNetdev(models.Model):
    _name = 'silver.netdev'
    #_table = 'isp_netdev'
    _description = 'ISP Network Device (Base Model)'

    #name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)

    netdev_type = fields.Selection([
        ('ap', 'AP'),
        ('core', 'Core'),
        ('nap', 'NAP'),
        ('olt', 'OLT'),
        ('port', 'Port'),
        ('radius', 'Radius'),
        ('other', 'Other')
    ], default='other')


    ip = fields.Char(string='IP de Conexion')
    port = fields.Char(string='Puerto de Conexion')
    username = fields.Char(string='Usuario')
    password = fields.Char(string='Password')
    type_connection = fields.Selection([("ssh","SSH"), ("telnet", "Telnet")], string='Tipo de Conexión')
    port_telnet = fields.Char(string='Puerto telnet', default=23)
    port_ssh = fields.Char(string='Puerto ssh', default=22)

    #api_hostname = fields.Char(string='Hostname/IP', required=True)
    api_port = fields.Integer(string='API Port', default=21000, required=True)


    state = fields.Selection([('down', 'Down'), ('active', 'Active'), ('connected', 'Connected'),
        ('connecting', 'Connecting'),
        ('disconnected', 'Disconnected'),
        ('error', 'Error')],

                             string='Estado', default='down')

    # Fields for Radius Client Configuration
    radius_client_ip = fields.Char(string='Radius Server IP')
    radius_client_secret = fields.Char(string='Radius Shared Secret')
    radius_client_services = fields.Many2many('silver.radius.service', string='Radius Services') # Assuming a model silver.radius.service exists or will be created

    core_ids = fields.One2many('silver.core', 'netdev_id', string='Cores')
    olt_ids = fields.One2many('silver.olt', 'netdev_id', string='OLTs')
    #olt_card_port_ids = fields.One2many('silver.olt.card.port', 'netdev_id', string='OLT Card Ports')
    #box_ids = fields.One2many('silver.box', 'netdev_id', string='Boxes')
    #ap_ids = fields.One2many('silver.ap', 'netdev_id', string='APs')
    #radius_ids = fields.One2many('silver.radius', 'netdev_id', string='Radius Servers')
    n_olt_id = fields.Many2one('silver.olt', string='OLT', compute='_compute_n_olt_id', store=False)
    n_core_id = fields.Many2one('silver.core', string='Core', compute='_compute_n_core_id', store=False)



    type_access_net = fields.Selection(
        [('inactive', 'Inactivo'), ('dhcp', 'DHCP Leases'), ('manual', 'IP Asignada manualmente'),
         ('system', 'IP Asiganada por el sistema')], default='inactive', string='Tipo Acceso', required=True)


    dhcp_custom_server = fields.Char(string='DHCP Leases')
    interface = fields.Char(string='Interface')
    is_dhcp_static = fields.Boolean(string='Habilitar Dhcp Static')
    dhcp_client = fields.Boolean(string='Profiles VSOL')


    @api.depends('olt_ids')
    def _compute_n_olt_id(self):
        for netdev in self:
            # Busca si existe una OLT que apunte a este netdev
            olt = self.env['silver.olt'].search([('netdev_id', '=', netdev.id)], limit=1)
            netdev.n_olt_id = olt or False


    @api.depends('core_ids')
    def _compute_n_core_id(self):
        for netdev in self:
            # Busca si existe una OLT que apunte a este netdev
            core = self.env['silver.core'].search([('netdev_id', '=', netdev.id)], limit=1)
            netdev.n_core_id = core or False





    def _get_olt_connection(self):
        self.ensure_one()
        return OLTConnection(
            host=self.ip,
            port=(self.port_ssh if self.type_connection=='ssh'  else self.port_telnet),
            username=self.username,
            password=self.password,
            connection_type=self.type_connection,
        )


    def get_formview_id(self, access_uid=None):
        self.ensure_one()
        if self.env['silver.core'].search([('netdev_id', '=', self.id)], limit=1):
            print(("escore", self.netdev_type,
                   self.env['silver.core'].search([('netdev_id', '=', self.id)], limit=1)))
            return self.env.ref('view_silver_core_form').id
        if self.env['silver.ap'].search([('netdev_id', '=', self.id)], limit=1):
            return self.env.ref('view_silver_ap_form').id
        return super().get_formview_id(access_uid=access_uid)