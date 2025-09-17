from odoo import models, fields, api

class IspCore(models.Model):
    _name = 'isp.core'
    _description = 'Equipo Core ISP'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    _inherits = {'isp.asset': 'asset_id',
                 'isp.netdev':'netdev_id'}

    asset_id = fields.Many2one('isp.asset', required=True, ondelete="cascade")
    netdev_id = fields.Many2one('isp.netdev', required=True, ondelete="cascade")


    name = fields.Char(related='asset_id.name', string='Nombre', required=False, readonly=False)

    hostname_core = fields.Char(string='Hostname')

    node_id = fields.Many2one('isp.node', string='Nodo')
    node_ids = fields.Many2many('isp.node', string='Nodos')


# --- Campos Base y Relaciones ---
#    name = fields.Char(string='Código', required=True)
    active = fields.Boolean(string='Activo', default=True)

    node_id = fields.Many2one('isp.node', string='Nodo')
    brand_id = fields.Many2one('product.brand', string='Marca', index=True)
   # gateway = fields.Many2one('isp.ip.address', string='Gateway')
    radius_id = fields.Many2one('isp.radius', string='Radius')
    networks_device_id = fields.Many2many('isp.device.networks', string='Networks Device')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)

    custom_channel_ids = fields.One2many('addres.list.channel.line', 'core_id', string='Canales')
    isp_core_port_line_ids = fields.One2many('isp.core.port.line', 'core_id', string='Líneas Puerto Slot')

    kex_algorithms_ids = fields.Many2many('isp.kex.algorithms', string='Kex Algorithms')
    networks_device_id = fields.Many2many('isp.device.networks', string='Equipos de red')
    isp_vlans_ids = fields.Many2many('isp.vlan', string='Vlans')
    pooOnlyCore = fields.Boolean(string='Pool de IPs Único')

    node_ids = fields.Many2many('isp.node', string='Nodos') # ¡Ojo con este, podría ser redundante!

    # --- Campos de Conectividad y Acceso ---
    user = fields.Char(string='Usuario')
    username = fields.Char(string='Usuario Core', readonly=False)
    user_nass = fields.Char(string='Usuario Nass')
    password = fields.Char(string='Password', related="netdev_id.password", readonly=False)
    password_nass = fields.Char(string='Password Nass')
    key_pppoe = fields.Char(string='Password PPPoE')

    port = fields.Char(string='Puerto de Conexión', related="netdev_id.port", readonly=False)
    port_coa = fields.Char(string='Puerto COA')
    ip = fields.Char(string='IP de Conexión', related="netdev_id.ip", readonly=False)
    hostname_core = fields.Char(string='Hostname')
    interface = fields.Char(string='Interface')
    cvlan = fields.Char(string='CVLAN')
    svlan = fields.Char(string='SVLAN')

    # --- Campos de Estado y Métricas (calculados) ---
    state = fields.Selection([('draft', 'Borrador'), ('active', 'Activo'),  ('down', 'Down')], string='Status')
    display_name = fields.Char(string='Display Name', compute='_compute_display_name')

    olt_count = fields.Integer(string='Conteo Equipo OLT', compute='_compute_counts')
    radius_count = fields.Integer(string='Conteo Servidor Radius', compute='_compute_counts')
    ap_count = fields.Integer(string='Conteo Equipo AP', compute='_compute_counts')
    contracts_cores_count = fields.Integer(string='Conteo Cores', compute='_compute_counts')
    
    # --- Campos de Configuración y Funcionalidades ---
    is_device_network = fields.Boolean(string='Equipos de infraestructura de red')
    is_fiber = fields.Boolean(string='Fibra Óptica')
    is_wifi = fields.Boolean(string='Medio Inalámbrico')
    is_isp_radius = fields.Boolean(string='Activar Radius',  default=True)
    is_mikrotik_radius = fields.Boolean(string='Mikrotik Radius')
    is_pppoe_profile = fields.Boolean(string='Profile PPPoE')
    is_key_pppoe = fields.Boolean(string='Clave PPPoE')
    is_pppoe_wifi = fields.Boolean(string='PPPoE Medio Inalámbrico')
    is_local_address_pppoe = fields.Boolean(string='Local Address PPPoE')
    is_product_pppoe_profile = fields.Boolean(string='Custom Product PPPoE Profile')
    is_used_dynamic_pool = fields.Boolean(string='Usar Pool Dinámico')

    is_custom_address_list = fields.Boolean(string='Custom Address Lists')
    is_product_address_list = fields.Boolean(string='Custom Product Address Lists')
    is_custom_address_list_channel = fields.Boolean(string='Custom Addrs Lst por Canal')
    is_reconnection_ip_address_list = fields.Boolean(string='Reconexión IP+Address-List')

    is_gestion_queue_parent = fields.Boolean(string='Gestión de Cola Padre')
    is_simple_queue = fields.Boolean(string='Simple Queues')
    is_queue_tree = fields.Boolean(string='Queue Tree')
    is_fttb_queue = fields.Boolean(string='FTTB')
    is_mangle = fields.Boolean(string='Mangle')

    is_multiple_vlans = fields.Boolean(string='Habilitar múltiples Vlans')
    is_unique_vlans = fields.Boolean(string='Vlans única')
    is_active_vlans = fields.Boolean(string='Activar Vlans Core')

    is_type_core_access = fields.Boolean(string='Acceso', default=True)
    is_type_core_bandwidth = fields.Boolean(string='Ancho de banda')

    is_desactive_core = fields.Boolean(string='Desactivar Core')
    is_desactive_olt = fields.Boolean(string='Desactivar OLT')
    is_cutoff_reconnection = fields.Boolean(string='Corte/Reconexión Servicio', default=True)
    cutoff_reconnection_ipaddress = fields.Boolean(string='IP Address')
    cutoff_reconnection_piloto = fields.Boolean(string='Name Contrato')

    is_extract_mac_core = fields.Boolean(string='Asignar MAC para CALLER ID')
    is_change_mac = fields.Boolean(string='Mostrar MAC')
    is_extract_ip_lease = fields.Boolean(string='Extraer IP Lease')
    is_extract_ip_arp = fields.Boolean(string='Extraer IP ARP')
    is_generate = fields.Boolean(string='Generado?')
    is_action_button = fields.Boolean(string='Ejecutado desde el Botón')

    # --- Campos de Datos Varios ---
    access_token = fields.Char(string='Security Token')
    access_url = fields.Char(string='Portal Access URL', readonly=False)
    access_warning = fields.Text(string='Access warning', readonly=False)

    custom_list_active = fields.Char(string='Activos')
    custom_list_cuttoff = fields.Char(string='Cortados')
    custom_list_layoff = fields.Char(string='Suspendidos')

    dhcp_custom_server = fields.Char(string='DHCP Leases')
    brand_description = fields.Text(string='Descripción', readonly=False)
    software_version = fields.Char(string='Versión Software')
    poolip = fields.Char(string='Poolip')
    user_profile_radius = fields.Char(string='User PROFILE')
    model = fields.Char(string='Modelo')

    slot = fields.Integer(string='Tarjeta Slot')
    port_card = fields.Integer(string='Puerto por Tarjeta')

    # --- Campos de Selección ---
    type_access_net = fields.Selection([('wired', 'Cableado'), ('wireless', 'Inalámbrico'), ('inactivo', 'Inactivo'), ('dhcp', 'IP Asiganada por el sistema')], string='Tipo')
    type_connection = fields.Selection([('router', 'Router'), ('switch', 'Switch'), ('ssh', 'ssh'), ('telnet', 'Telnet')], string='Tipo de Conexión')
    type_manager_address_list = fields.Selection([], string='Tipos de Control')

    # --- Relacionado al mixin de asset ---
    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='core',
        store=True,
        readonly=False
    )
    netdev_type = fields.Selection(
        related='netdev_id.netdev_type',
        default='core',
        store=True,
        readonly=False
    )

    @api.depends('name', 'company_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.name} ({record.company_id.name})" if record.company_id else record.name
    @api.model
    def create(self, vals):
        if vals.get('node_id'):
            node = self.env['isp.node'].browse(vals['node_id'])
            if node.exists() and node.code:

                core_count = self.search_count([('node_id', '=', node.id)])

                vals['parent_id'] = node.asset_id.id
                vals['name'] = f"{node.code}/CR{core_count + 1}"
        return super(IspCore, self).create(vals)


    def write(self, vals):
        print(("corewrite", vals))
        for i, record in enumerate(self):
            if vals.get('node_id'):
                node = self.env['isp.node'].browse(vals['node_id'])
            else:
                node = record.node_id

            if node.exists() and node.code:
                # This logic handles single and multiple record updates.
                # For multiple updates, it iterates and assigns a unique incremental name to each.
                base_count = self.search_count([('node_id', '=', node.id)])

                print(("cocrewr1", record.asset_id.id, record.parent_id, vals))

                if (not record.parent_id ) or (record.parent_id.id != node.asset_id.id):
                    record.parent_id = node.asset_id.id


                record.asset_id.name = f"{node.code}/CR{base_count + i + 1}"
            print(("cocrewr2", record.asset_id.name))
        return super(IspCore, self).write(vals)

    #@api.depends('olt', 'radius', 'ap_count', 'cor')
    def _compute_counts(self):
        print(("_compute_counts", self))
        for record in self:
            record.olt_count = self.env['isp.olt'].search_count([('core_id', '=', record.id)])
            record.radius_count = self.env['isp.radius'].search_count([('core_id', '=', record.id)])
            record.ap_count = self.env['isp.ap'].search_count([('node_ids', 'in', record.node_ids.ids)])
            record.contracts_cores_count = self.env['isp.contract'].search_count([('core_id', '=', record.id)])

    @api.model
    def default_get(self, fields_list):
        res = super(IspCore, self).default_get(fields_list)
        rr = self.search([('radius_id', '!=', False)])
        r = self.search([('radius_id', '!=', False)], limit=1)

        # Set a default partner_id and payment_term_id
        res['radius_id'] = r.radius_id.id
        res['networks_device_id'] = r.networks_device_id
        res['company_id'] = r.company_id
        res['user_nass'] = r.user_nass
        res['password_nass'] =r.password_nass
        res['port_coa'] = r.port_coa

        print(("default", res, r, rr))
        return res


    def create_ap(self):
        self.ensure_one()
        new_ap = self.env['isp.ap'].create({
           #   'name': f"AP for {self.name}",
            'core_id': self.id,
        })
        return {
            'name': 'AP Creado',
            'type': 'ir.actions.act_window',
            'res_model': 'isp.ap',
            'view_mode': 'form',
            'res_id': new_ap.id,
            'target': 'current',
        }

    def create_radius(self):
        self.ensure_one()
        new_radius = self.env['isp.radius'].create({
            #'name': f"Radius for {self.name}",
            'core_id': self.id,
        })
        return {
            'name': 'Radius Creado',
            'type': 'ir.actions.act_window',
            'res_model': 'isp.radius',
            'view_mode': 'form',
            'res_id': new_radius.id,
            'target': 'current',
        }

    def action_create_nas(self):
        self.ensure_one()
        # Simulate creating NAS
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Create NAS',
                'message': 'NAS created successfully!',
                'type': 'success',
            }
        }

    def action_remove_nas(self):
        self.ensure_one()
        # Simulate removing NAS
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Remove NAS',
                'message': 'NAS removed successfully!',
                'type': 'success',
            }
        }

    def action_connect_core(self):
        self.ensure_one()
        # Simulate connection test
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Connection Test',
                'message': 'Connection to Core was successful!',
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

    def action_calculate_gpon(self):
        self.ensure_one()
        # Simulate calculating GPON
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Calculate GPON',
                'message': 'GPON calculated successfully!',
                'type': 'success',
            }
        }

    def action_view_olts(self):
        self.ensure_one()
        return {
            'name': 'Equipos OLT',
            'type': 'ir.actions.act_window',
            'res_model': 'isp.olt',
            'view_mode': 'tree,form',
            'domain': [('core_id', '=', self.id)],
            'context': {'default_core_id': self.id},
            'target': 'current',
        }

    def action_view_radius(self):
        self.ensure_one()
        return {
            'name': 'Radius',
            'type': 'ir.actions.act_window',
            'res_model': 'isp.radius',
            'view_mode': 'tree,form',
            'domain': [('core_id', '=', self.id)],
            'context': {'default_core_id': self.id},
            'target': 'current',
        }

    def action_view_aps(self):
        self.ensure_one()
        return {
            'name': 'Equipos AP',
            'type': 'ir.actions.act_window',
            'res_model': 'isp.ap',
            'view_mode': 'tree,form',
            'domain': [('core_id', '=', self.id)],
            'context': {'default_core_id': self.id},
            'target': 'current',
        }

    def action_view_contracts(self):
        self.ensure_one()
        return {
            'name': 'Contratos',
            'type': 'ir.actions.act_window',
            'res_model': 'isp.contract',
            'view_mode': 'tree,form',
            'domain': [('core_id', '=', self.id)],
            'context': {'default_core_id': self.id},
            'target': 'current',
        }

    def button_test_connection(self):
        si = False
        for core in self:
            if core.netdev_id:
                try:
                    is_successful = core.netdev_id.button_test_connection()
                    if is_successful:
                        core.state = 'active'
                        si=True
                    else:
                        core.state = 'down'
                except Exception:
                    core.state = 'down'
            else:
                core.state = 'down'
        if si:
            return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Connection Test',
                'message': 'Connection to Radius server was successful!',
                'type': 'success',
            }
        }


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
