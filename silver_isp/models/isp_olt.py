from odoo import models, fields

class IspOlt(models.Model):
    _name = 'isp.olt'
    _description = 'Equipo OLT'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'isp.asset': 'asset_id'}

    asset_id = fields.Many2one('isp.asset', required=True, ondelete='cascade')

    hostname_olt = fields.Char(string='Hostname', compute='_compute_hostname', store=True, readonly=True)


    software_version = fields.Char(string='Version Software')
    is_core_baudcom = fields.Boolean(string='Es Baudcom?')
    core_ids = fields.Many2many('isp.core', string='Equipos Core')
    bridge_core_id = fields.Many2one('isp.core', string='Equipo Core')
    is_vsol_marca = fields.Boolean(string='Es VSOL Marca?')
    is_brand_zte = fields.Boolean(string='Es Marca ZTE?')
    core_id = fields.Many2one('isp.core', string='Equipo Core')
    node_id = fields.Many2one('isp.node', string='Nodo')
    num_slot_olt = fields.Integer(string='Numero de Slots')
    ip_olt = fields.Char(string='IP de Conexion')
    port_olt = fields.Integer(string='Puerto de Conexion')
    type_connection = fields.Selection([("ssh","SSH"), ("telnet", "Telnet")], string='Tipo de Conexión')
    kex_algorithms_ids = fields.Many2many('isp.kex.algorithms', string='Kex Algorithms')
    is_multi_user_olt = fields.Boolean(string='Multiples Usuarios')
    user_olt = fields.Char(string='Usuario')
    password_olt = fields.Char(string='Password')
    secret_olt = fields.Char(string='Secret')
    is_pppoe = fields.Boolean(string='PPPoE')
    is_ipoe = fields.Boolean(string='IPoE')
    is_mgn_service_port = fields.Boolean(string='Puerto/IP para Gestion')
    ges_gemport = fields.Char(string='gemport')
    g_name_service = fields.Char(string='Name Service')
    is_custom_tcont = fields.Boolean(string='Custom Tcont')
    tcont = fields.Char(string='Tcont')
    is_custom_gempor = fields.Boolean(string='Custom Gemport')
    gemport = fields.Char(string='Gemport')
    is_line_nap = fields.Boolean(string='Gestion Vlan NAP')
    is_gestion_pppoe = fields.Boolean(string='Gestión WAN ONU')
    is_extract_mac_onu = fields.Boolean(string='Extraer MAC ONU')
    is_control_mac_learn = fields.Boolean(string='Extraer MAC Learn')
    is_activation_bridge = fields.Boolean(string='Activacion Bridge')
    is_cutoff_reconnection = fields.Boolean(string='Corte/Reconexion Servicio')
    is_disable_onu = fields.Boolean(string='Deshabilitar ONU')
    is_shutdown_interface = fields.Boolean(string='Shutdown Interface')
    is_cutoff_port = fields.Boolean(string='Corte Por Puerto')
    is_reduce_script = fields.Boolean(string='Script Reducido')
    is_redirect_srvport = fields.Boolean(string='Redireccionamiento ServicePort')
    is_active_wan_onu = fields.Boolean(string='Activar WAN ONU')
    ont_srvprofile = fields.Selection([('name', 'Name'),('id', 'ID'), ('port','ID por puerto')], string='Ont Srvprofile')
    ont_srvprofile_value = fields.Char(string='Valor ont_srvprofile')
    ont_lineprofile = fields.Selection([('name', 'Name'),('id', 'ID'), ('unique','ID unico')], string='Ont Lineprofile')
    ont_lineprofile_value = fields.Char(string='Valor ont_lineprofile')
    send_srvprofile = fields.Boolean(string='Send Srvprofile')
    port_vlan = fields.Boolean(string='Port Vlan')
    wan_maximum = fields.Boolean(string='WAN Maxima')
    name_service = fields.Char(string='Name Server')
    type_access_net = fields.Selection([('inactive', 'Inactivo'), ('dhcp', 'DHCP Leases'), ('manual', 'IP Asignada manualmente'), ('system', 'IP Asignada por el sistema')],  default='inactive', string='Tipo Acceso', required=True)
    dhcp_custom_server = fields.Char(string='DHCP Leases')
    traffic_table = fields.Selection([('name', 'Name'), ('index', 'Index')], string='Traffic-Table(command)')
    is_control_traffic_profile = fields.Boolean(string='Control por Traffic Profile')
    is_not_user_encap_ipoe = fields.Boolean(string='Disable Encapsulamiento IPOE/PPPOE')
    is_uplink_port_vlan = fields.Boolean(string='Uplink Port VLAN')
    is_product_vlan = fields.Boolean(string='Vlans-Profiles por Producto')
    is_custom_pon_vlan = fields.Boolean(string='Gestion PON por Vlan')
    service_port_internet = fields.Char(string='Service Port-Internet')
    description = fields.Text(string='Descripción')
    is_control_bandwidth = fields.Boolean(string='Controlar Ancho de Banda')
    is_control_upstream = fields.Boolean(string='Controlar Upstream')
    profile_onu_generic = fields.Char(string='Profile ONU Generico')
    profile_dba_gestion = fields.Char(string='Profile DBA de Gestion')
    profile_dba_internet = fields.Char(string='Profile DBA de Internet')
    dhcp_client = fields.Boolean(string='Profiles VSOL')
    is_serial_onu_hex = fields.Boolean(string='Serial Onu Hexadecimal')
    is_serial_onu_ascii = fields.Boolean(string='Serial Onu ASCII')
    is_virtual = fields.Boolean(string='Virtual')

    isp_core_port_line_id = fields.Many2one('isp.core.port.line', string='Interface Core')
    is_active_tr = fields.Boolean(string='Activar TR-069')
    is_v2_brand_zte = fields.Boolean(string='Es Version 2 Zte?')
    primary_dns = fields.Char(string='DNS Primario')
    secondary_dns = fields.Char(string='DNS Secundario')
    is_write_olt = fields.Boolean(string='Guardar Configuracion Olt')
    is_enable_remote_access_onu = fields.Boolean(string='Habilitar Acceso Remoto ONU')
    line_olt_product = fields.One2many('olt.line.product', 'olt_id', string='line product')
    ip_address_line_ids = fields.One2many('isp.ip.address.line', 'olt_id', string='Direcciones IP')
    ip_address_ids = fields.One2many('isp.ip.address', 'olt_id', string='Direcciones IP')
    users_olt_ids = fields.One2many('isp.olt.users', 'olt_id', string='Usuarios Equipo OLT')
    pri_onu_standar = fields.Char(string='PRI ONU Standar:')
    pri_onu_bridge = fields.Char(string='PRI ONU Bridge:')
    connection_wan = fields.Selection([('pppoe', 'PPPoE'), ('dhcp','DHCP'), ('static', 'IP estática')], string='Modo de conexión WAN')
    protocol_type = fields.Selection([('ipv4', 'IPv4')], string='Protocolo Type')
    wan_mode = fields.Selection([('router', 'Router'), ('bridge', 'Bridge')], string='WAN Mode')
    service_type = fields.Selection([('void', 'VOID'), ('internet', 'INTERNET')], string='Service Type')
    acquisition_mode = fields.Selection([('pppoe', 'PPPoE'), ('dhcp','DHCP'), ('static', 'IP estática')], string='IP Acquisition Mode')
    vlan_id = fields.Char(string='VLAN ID')
    mtu = fields.Char(string='MTU')
    is_enable_nat = fields.Boolean(string='Enable NAT')
    is_disabled_dhcp_pv4 = fields.Boolean(string='Deshabilitar Dhcp IPv6')
    is_control_admin = fields.Boolean(string='Admin Control')
    admin_user = fields.Char(string='Admin User')
    password_user = fields.Char(string='Password User')
    lan1 = fields.Boolean(string='Lan1')
    lan2 = fields.Boolean(string='Lan2')
    lan3 = fields.Boolean(string='Lan3')
    lan4 = fields.Boolean(string='Lan4')
    ssid1 = fields.Boolean(string='SSID1')
    ssid2 = fields.Boolean(string='SSID2')
    ssid3 = fields.Boolean(string='SSID3')
    ssid4 = fields.Boolean(string='SSID4')
    ssid5 = fields.Boolean(string='SSID5')
    ssid6 = fields.Boolean(string='SSID6')
    ssid7 = fields.Boolean(string='SSID7')
    ssid8 = fields.Boolean(string='SSID8')
    isp_tr_069_id = fields.Many2one('isp.tr.069', string='Servidor TR-069')
    vlan_mgn_tr069 = fields.Integer(string='Vlan Mgn_TR69')
    ip_address_line_tr69_ids = fields.One2many('isp.ip.address.line', 'olt_id', string='Direcciones IP', domain=[('is_tr_069', '=', True)])
    ip_address_tr69_ids = fields.One2many('isp.ip.address', 'olt_id', string='Direcciones IP', domain=[('is_tr_069', '=', True)])
    state = fields.Selection([('down', 'Down'), ('active', 'Active')], string='Estado', default='down')
    olt_card_count = fields.Integer(string='Conteo Slot OLT', compute='_compute_olt_card_count')
    contracts_olt_count = fields.Integer(string='Conteo Olts', compute='_compute_contracts_olt_count')



    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='olt',
        store=True,
        readonly=False
    )

    def _compute_hostname(self):
        for olt in self:
            if olt.node_id:
                # Contamos los OLTs existentes para este nodo
                # Esto es la clave para el incremental por nodo
                olt_count = self.env['isp.olt'].search_count([('node_id', '=', olt.node_id.id)])

                # Construimos el código.
                # Si el campo 'code' del nodo es 'u', y ya tiene 2 OLTs, el nuevo será 'u/2'
                olt.code = f"{olt.node_id.code}/{olt.node_id.node}{olt_count}"
            else:
                olt.code = False

    def _compute_olt_card_count(self):
        self.olt_card_count = 0

    def _compute_contracts_olt_count(self):
        self.contracts_olt_count = 0

    def create_olt_card(self):
        self.ensure_one()
        new_card = self.env['isp.olt.card'].create({
            'name': f"Card for {self.name}",
            'olt_id': self.id,
        })
        return {
            'name': 'OLT Card Creada',
            'type': 'ir.actions.act_window',
            'res_model': 'isp.olt.card',
            'view_mode': 'form',
            'res_id': new_card.id,
            'target': 'current',
        }

    def action_connect_olt(self):
        self.ensure_one()
        # Simulate connection test
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Connection Test',
                'message': 'Connection to OLT was successful!',
                'type': 'success',
            }
        }

    def action_create_profile_olt(self):
        self.ensure_one()
        # Simulate profile creation
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Profile Creation',
                'message': 'Profiles created successfully!',
                'type': 'success',
            }
        }

    def action_send_password(self):
        self.ensure_one()
        # Simulate sending password
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Send Password',
                'message': 'Password sent successfully!',
                'type': 'success',
            }
        }
