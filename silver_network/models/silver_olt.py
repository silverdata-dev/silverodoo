from odoo import models, fields, api
from odoo.exceptions import UserError

class SilverOlt(models.Model):
    _name = 'silver.olt'
    _description = 'Equipo OLT'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name_sequence = 'silver.olt.sequence'
    #_table = 'isp_olt'

    _inherits = {'silver.asset': 'asset_id',
                 'silver.netdev':'netdev_id'}

    asset_id = fields.Many2one('silver.asset', required=True, ondelete="cascade")
    netdev_id = fields.Many2one('silver.netdev', required=True, ondelete="cascade")



    hostname_olt = fields.Char(string='Hostname')
    name = fields.Char('Nombre', related='asset_id.name', compute='_compute_hostname', store=True, readonly=True)



    is_core_baudcom = fields.Boolean(string='Es Baudcom?')
    core_ids = fields.Many2many('silver.core', string='Equipos Core')
    bridge_core_id = fields.Many2one('silver.core', string='Equipo b Core')
    is_vsol_marca = fields.Boolean(string='Es VSOL Marca?')
    is_brand_zte = fields.Boolean(string='Es Marca ZTE?')
    core_id = fields.Many2one('silver.core', string='Equipo Core')
    node_id = fields.Many2one('silver.node', string='Nodo')
    num_slot_olt = fields.Integer(string='Numero de Slots')
    num_ports1 = fields.Selection([
        ('8', '8 Puertos'),
        ('16', '16 Puertos'),
        ('32', '32 Puertos'),
        ('64', '64 Puertos'),
    ], string='Cantidad de Puertos 0', default="8")
    num_ports2 = fields.Selection([
        ('8', '8 Puertos'),
        ('16', '16 Puertos'),
        ('32', '32 Puertos'),
        ('64', '64 Puertos'),
    ], string='Cantidad de Puertos 0', default="8")
    num_ports3 = fields.Selection([
        ('8', '8 Puertos'),
        ('16', '16 Puertos'),
        ('32', '32 Puertos'),
        ('64', '64 Puertos'),
    ], string='Cantidad de Puertos 0', default="8")
    num_ports4 = fields.Selection([
        ('8', '8 Puertos'),
        ('16', '16 Puertos'),
        ('32', '32 Puertos'),
        ('64', '64 Puertos'),
    ], string='Cantidad de Puertos 0', default="8")
    num_ports5 = fields.Selection([
        ('8', '8 Puertos'),
        ('16', '16 Puertos'),
        ('32', '32 Puertos'),
        ('64', '64 Puertos'),
    ], string='Cantidad de Puertos 0', default="8")

    kex_algorithms_ids = fields.Many2many('silver.kex.algorithms', string='Kex Algorithms')
    is_multi_user_olt = fields.Boolean(string='Multiples Usuarios')

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

    silver_core_port_line_id = fields.Many2one('silver.core.port.line', string='Interface Core')
    is_active_tr = fields.Boolean(string='Activar TR-069')
    is_v2_brand_zte = fields.Boolean(string='Es Version 2 Zte?')
    primary_dns = fields.Char(string='DNS Primario')
    secondary_dns = fields.Char(string='DNS Secundario')
    is_write_olt = fields.Boolean(string='Guardar Configuracion Olt')
    is_enable_remote_access_onu = fields.Boolean(string='Habilitar Acceso Remoto ONU')
    line_olt_product = fields.One2many('olt.line.product', 'olt_id', string='line product')
    users_olt_ids = fields.One2many('silver.olt.users', 'olt_id', string='Usuarios Equipo OLT')
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
    silver_tr_069_id = fields.Many2one('silver.tr.069', string='Servidor TR-069')
    vlan_mgn_tr069 = fields.Integer(string='Vlan Mgn_TR69')
#    ip_address_pool_tr69_ids = fields.One2many('silver.ip.address.pool', 'olt_id', string='Direcciones IP', domain=[('is_tr_069', '=', True)])
#    ip_address_tr69_ids = fields.One2many('silver.ip.address', 'olt_id', string='Direcciones IP', domain=[('is_tr_069', '=', True)])
    state = fields.Selection([('down', 'Down'), ('active', 'Active')], string='Estado', default='down')
    olt_card_count = fields.Integer(string='Conteo Slot OLT', compute='_compute_olt_card_count')
    #contracts_olt_count = fields.Integer(string='Conteo Olts', compute='_compute_contracts_olt_count')
    ip_range_count = fields.Integer(string='IP Ranges', compute='_compute_ip_range_count')
    isp_tr_069_id = fields.Many2one("isp.tr.069", string="Equipo OLT")

#    "ip_address_line_tr69_ids", "Direcciones IP", "Equipo OLT", "one2many", "Campo base", "", "True", "", "isp.ip.address.line"

    olt_card_port_count = fields.Integer(string='Conteo Puertos', compute='_compute_counts')


    port_ids = fields.One2many('silver.olt.card.port', 'olt_id', string='Puertos')
    card_ids = fields.One2many('silver.olt.card', 'olt_id', string='Tarjetas')

    def _compute_olt_card_port_count(self):
        for record in self:
            record.olt_card_port_count = self.env['silver.olt.card.port'].search_count([('olt_id', '=', record.id)])




    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='olt',
        store=True,
        readonly=False
    )

    netdev_type = fields.Selection(
        related='netdev_id.netdev_type',
        default='olt',
        store=True,
        readonly=False
    )


    type_access_net = fields.Selection(
       
        [('inactive', 'Inactivo'), ('dhcp', 'DHCP Leases'), ('manual', 'IP Asignada manualmente'),
         ('system', 'IP Asignada por el sistema')], 
          related='netdev_id.type_access_net',
         default='inactive', string='Tipo Acceso', required=True)


    @api.model
    def create(self, vals):
        print(("createee", vals))
        if vals.get('core_id'):
            core = self.env['silver.core'].browse(vals['core_id'])
            print(("createee0", core, core.name, core.asset_id, core.asset_id.name))
            if core.exists() and core.name and  not vals.get("name"):
                olt_count = self.search_count([('core_id', '=', core.id)])
                vals['name'] = f"{core.name}/OLT{olt_count + 1}"
                print(("createe2e", vals))
        print(("createee3", vals))
        return super(SilverOlt, self).create(vals)


    def write(self, vals):
        print(("apwrite", vals))

        for i, record in enumerate(self):
            if vals.get('coreid'):
                core = self.env['silver.core'].browse(vals['core_id'])
            else:
                core = record.core_id

            if core.exists() and core.name:
                olt_count = self.search_count([('core_id', '=', core.id)])
                record.asset_id.name = f"{core.name}/OLT{olt_count + 1}"


            # If node_id is set to False, the name is not changed.
        return super(SilverOlt, self).write(vals)



   # @api.onchange('num_slot_olt', 'num_ports1', 'num_ports2', 'num_ports3', 'num_ports4', 'num_ports5')
    def action_generar(self):
        if self.num_slot_olt > 5:
            self.num_slot_olt = 5
            return {
                'warning': {
                    'title': "Límite Excedido",
                    'message': "El número de slots no puede ser mayor a 5. Se ha ajustado automáticamente a 5.",
                }
            }

        num_ports_fields = [int(self.num_ports1), int(self.num_ports2), int(self.num_ports3), int(self.num_ports4), int(self.num_ports5)]

        # Crear tarjetas faltantes de forma aditiva
        current_card_count = len(self.card_ids)
        for i in range(current_card_count, self.num_slot_olt):
            new_card = self.env['silver.olt.card'].new({
                'name': f'{self.name}/C{i}',
                'olt_id': self._origin.id,
                'num_card': i,
            })
            self.card_ids += new_card

        # Crear puertos faltantes para cada tarjeta de forma aditiva
        for i, card in enumerate(self.card_ids):
            if i >= self.num_slot_olt:
                continue

            target_port_count = num_ports_fields[i] if i < len(num_ports_fields) else 0
            current_port_count = len(card.port_ids)
            if (i == 0) and (current_port_count == 0):
                for p in self.port_ids:
                    p.olt_card_id = card
                    card.port_ids += p
                current_port_count = len(card.port_ids)

            for j in range(current_port_count, target_port_count):
                new_port = self.env['silver.olt.card.port'].new({
                    'name':  f'{card.name}/P{j+1}',
                    'olt_id': self._origin.id,
                    'olt_card_id': card._origin.id,
                    'olt_card_n':i,
                    'num_port':j+1,

                })
                card.port_ids += new_port


    def _compute_hostname(self):
        for olt in self:
            if olt.node_id:
                # Contamos los OLTs existentes para este nodo
                # Esto es la clave para el incremental por nodo
                olt_count = self.env['silver.olt'].search_count([('node_id', '=', olt.node_id.id)])

                # Construimos el código.
                # Si el campo 'code' del nodo es 'u', y ya tiene 2 OLTs, el nuevo será 'u/2'
                olt.name = f"{olt.node_id.code}/{olt.node_id.node}{olt_count}"
            else:
                olt.name = False

    def _compute_olt_card_count(self):
        for record in self:
            record.olt_card_count = self.env['silver.olt.card'].search_count([('olt_id', '=', record.id)])

    def _compute_ip_range_count(self):
        for record in self:
            record.ip_range_count = self.env['silver.ip.address'].search_count([('olt_id', '=', record.id)])

    def create_olt_card(self):
        self.ensure_one()
        new_card = self.env['silver.olt.card'].create({
#            'name': f"Card for {self.name}",
            'olt_id': self.id,
        })
        return {
            'name': 'OLT Card Creada',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.olt.card',
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

    def action_view_olt_cards(self):
        self.ensure_one()
        return {
            'name': 'Tarjetas OLT',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.olt.card',
            'view_mode': 'tree,form',
            'domain': [('olt_id', '=', self.id)],
            'context': {'default_olt_id': self.id},
            'target': 'current',
        }
    def generar(self):
        for record in self:
            record.netdev_id.generar()