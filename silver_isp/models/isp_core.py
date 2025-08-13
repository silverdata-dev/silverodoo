from odoo import models, fields, api

class IspCore(models.Model):
    _name = 'isp.core'
    _description = 'Equipo Core ISP'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    _inherits = {'isp.asset': 'asset_id',
                 'isp.netdev':'netdev_id'}

    asset_id = fields.Many2one('isp.asset', required=True, ondelete="cascade")
    netdev_id = fields.Many2one('isp.netdev', required=True, ondelete="cascade")


    name = fields.Char(related='asset_id.name', string='Código', required=True, copy=False, default=lambda self: ('Nuevo'))

    hostname_core = fields.Char(string='Hostname')

    node_id = fields.Many2one('isp.node', string='Nodo')
    node_ids = fields.Many2many('isp.node', string='Nodos')

    is_isp_radius = fields.Boolean(string='Activar Radius')
    radius_id = fields.Many2one('isp.radius', string='Radius')
    networks_device_id = fields.Many2many('isp.device.networks', string='Networks Device')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    user_nass = fields.Char(string='Usuario Nass')
    password_nass = fields.Char(string='Password Nass')
    port_coa = fields.Char(string='Puerto COA')
    

    kex_algorithms_ids = fields.Many2many('isp.kex.algorithms', string='Kex Algorithms')



    is_multiple_vlans = fields.Boolean(string='Habilitar multiples Vlans')

    is_active_vlans = fields.Boolean(string='Activar Vlans Core')
    cvlan = fields.Char(string='CVLAN')
    svlan = fields.Char(string='SVLAN')
    isp_vlans_ids = fields.Many2many('isp.vlan', string='Vlans')
    is_device_network = fields.Boolean(string='Equipos de infraestructura de red')

    olt_count = fields.Integer(string='Conteo Equipo OLT', compute='_compute_counts')
    radius_count = fields.Integer(string='Conteo Servidor Radius', compute='_compute_counts')
    ap_count = fields.Integer(string='Conteo Equipo AP', compute='_compute_counts')
    contracts_cores_count = fields.Integer(string='Conteo Cores', compute='_compute_counts')
    
    # --- Campos de la pestaña de Configuraciones ---
    is_extract_mac_core = fields.Boolean(string='Asignar MAC para CALLER ID')
    cutoff_reconnection_ipaddress = fields.Boolean(string='IP Address')
    cutoff_reconnection_piloto = fields.Boolean(string='Name Contrato')
    pooOnlyCore = fields.Boolean(string='Pool de IPs Único')
    is_type_core_access = fields.Boolean(string='Acceso')
    is_type_core_bandwidth = fields.Boolean(string='Ancho de banda')
    is_fiber = fields.Boolean(string='Fibra Óptica')
    is_wifi = fields.Boolean(string='Medio Inalámbrico')
    is_fttb_queue = fields.Boolean(string='FTTB')
    is_change_mac = fields.Boolean(string='Mostrar MAC')
    is_extract_ip_lease = fields.Boolean(string='Extraer IP Lease')
    is_extract_ip_arp = fields.Boolean(string='Extraer IP ARP')
    is_mikrotik_radius = fields.Boolean(string='Mikrotik Radius')
    user_profile_radius = fields.Char(string='User PROFILE')
    is_simple_queue = fields.Boolean(string='Simple Queues')
    is_gestion_queue_parent = fields.Boolean(string='Gestión de Cola Padre')
    is_queue_tree = fields.Boolean(string='Queue Tree')
    is_mangle = fields.Boolean(string='Mangle')
    type_manager_address_list = fields.Selection([], string='Tipos de Control')
    is_cutoff_reconnection = fields.Boolean(string='Corte/Reconexión Servicio')
    is_reconnection_ip_address_list = fields.Boolean(string='Reconexión IP+Address-List')
    is_custom_address_list_channel = fields.Boolean(string='Custom Addrs Lst por Canal')
    is_custom_address_list = fields.Boolean(string='Custom Address Lists')
    custom_list_active = fields.Char(string='Activos')
    custom_list_cuttoff = fields.Char(string='Cortados')
    custom_list_layoff = fields.Char(string='Suspendidos')
    is_product_address_list = fields.Boolean(string='Custom Product Address Lists')
    is_pppoe_wifi = fields.Boolean(string='PPPoE Medio Inalámbrico')
    is_key_pppoe = fields.Boolean(string='Clave PPPoE')
    key_pppoe = fields.Char(string='Password')
    is_used_dynamic_pool = fields.Boolean(string='Usar Pool Dinámico')
    is_local_address_pppoe = fields.Boolean(string='Local Address PPPoE')
    is_pppoe_profile = fields.Boolean(string='Profile PPPoE')
    is_product_pppoe_profile = fields.Boolean(string='Custom Product PPPoE Profile')
    custom_channel_ids = fields.One2many('addres.list.channel.line', 'core_id', string='Canales')
    is_unique_vlans = fields.Boolean(string='Vlans única')
    is_desactive_core = fields.Boolean(string='Desactivar Core')
    is_desactive_olt = fields.Boolean(string='Desactivar OLT')

    slot = fields.Integer(string='Tarjeta Slot')
    port_card = fields.Integer(string='Puerto por Tarjeta')
    isp_core_port_line_ids = fields.One2many('isp.core.port.line', 'core_id', string='Lineas Puerto Slot')


    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='core',
        store=True,
        readonly=False
    )

    @api.model
    def create(self, vals):
        if vals.get('node_id'):
            node = self.env['isp.node'].browse(vals['node_id'])
            if node.exists() and node.code:
                core_count = self.search_count([('node_id', '=', node.id)])
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
            'name': f"Radius for {self.name}",
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
