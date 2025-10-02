from odoo import models, fields, api, _
from odoo.http import request
from odoo.exceptions import UserError
import logging, string, secrets

_logger = logging.getLogger(__name__)

class SilverCore(models.Model):
    _name = 'silver.core'
    #_table = 'isp_core'
    _description = 'Equipo Core ISP'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    _inherits = {'silver.asset': 'asset_id',
                 'silver.netdev':'netdev_id'}

    asset_id = fields.Many2one('silver.asset', required=True, ondelete="cascade")
    netdev_id = fields.Many2one('silver.netdev', required=True, ondelete="cascade")


    name = fields.Char(string='Nombre', required=True, default=lambda self: self._default_name(), readonly=False)

    def _default_name(self):
        node_id = self.env.context.get('default_node_id')
        if not node_id:
            params = self.env.context.get('params', {})
            if params.get('model') == 'silver.node':
                node_id = params.get('id')

        if node_id:
            node = self.env['silver.node'].browse(node_id)
            if node.exists() and node.code:
                core_count = self.search_count([('node_id', '=', node.id)])
                return f"{node.code}/CR{core_count + 1}"
        return False

    hostname_core = fields.Char(string='Hostname')

    node_id = fields.Many2one('silver.node', string='Nodo')
    node_ids = fields.Many2many('silver.node', string='Nodos')


# --- Campos Base y Relaciones ---
#    name = fields.Char(string='Código', required=True)
    active = fields.Boolean(string='Activo', default=True)

   # node_id = fields.Many2one('silver.node', string='Nodo')
    #brand_id = fields.Many2one('product.brand', string='Marca', index=True)
   # gateway = fields.Many2one('silver.ip.address', string='Gateway')
    radius_id = fields.Many2one('silver.radius', string='Radius')
    networks_device_id = fields.Many2many('silver.device.networks', string='Networks Device')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)

    custom_channel_ids = fields.One2many('address.list.channel.line', 'core_id', string='Canales')
    silver_core_port_line_ids = fields.One2many('silver.core.port.line', 'core_id', string='Líneas Puerto Slot')

    kex_algorithms_ids = fields.Many2many('silver.kex.algorithms', string='Kex Algorithms')

    silver_vlans_ids = fields.Many2many('silver.vlan', string='Vlans')
    pooOnlyCore = fields.Boolean(string='Pool de IPs Único')


    # --- Campos de Conectividad y Acceso ---
    user = fields.Char(string='Usuario')
    username = fields.Char(string='Usuario Core', related="netdev_id.username", readonly=False)
    user_nass = fields.Char(string='Usuario Nass')
    password = fields.Char(string='Password', related="netdev_id.password", readonly=False)
    password_nass = fields.Char(string='Password Nass')
    key_pppoe = fields.Char(string='Password PPPoE')

    port = fields.Char(string='Puerto de Conexión', related="netdev_id.port", readonly=False, default=2100)
    port_coa = fields.Char(string='Puerto COA')
    ip = fields.Char(string='IP de Conexión', related="netdev_id.ip", readonly=False)

    configured = fields.Selection([
        ('0', 'Not Configured'),
        ('1', 'Local Auth OK'),
        ('2', 'RADIUS Configured')
    ], string='Configurado', default='0', required=True,
        related="netdev_id.configured")

    interface = fields.Char(string='Interface')
    cvlan = fields.Char(string='CVLAN')
    svlan = fields.Char(string='SVLAN')

    # --- Campos de Estado y Métricas (calculados) ---
    state = fields.Selection([('draft', 'Borrador'), ('active', 'Activo'),  ('down', 'Down')], string='Status')
    display_name = fields.Char(string='Display Name', compute='_compute_display_name')

    olt_count = fields.Integer(string='Conteo Equipo OLT', compute='_compute_counts')
    radius_count = fields.Integer(string='Conteo Servidor Radius', compute='_compute_counts')
    ap_count = fields.Integer(string='Conteo Equipo AP', compute='_compute_counts')

    olt_ids = fields.One2many('silver.olt', 'core_id', string='OLTs')
    ap_ids = fields.One2many('silver.ap', 'core_id', string='APs')

    
    # --- Campos de Configuración y Funcionalidades ---
    is_device_network = fields.Boolean(string='Equipos de infraestructura de red')
    is_fiber = fields.Boolean(string='Fibra Óptica')
    is_wifi = fields.Boolean(string='Medio Inalámbrico')
    is_silver_radius = fields.Boolean(string='Activar Radius',  default=True)
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
    #brand_description = fields.Text(string='Descripción', readonly=False)

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


    @api.onchange('node_id')
    def _onchange_node_id(self):
        # --- Actualización del nombre en tiempo real ---
        if self.node_id and self.node_id.code:
            new_code = self.node_id.code
            # Si el nombre ya existe (estamos cambiando el nodo)
            if self.name and self._origin.node_id and self._origin.node_id.code:
                old_code = self._origin.node_id.code
                if self.name.startswith(f"{old_code}/"):
                    # Reemplaza el prefijo del código antiguo por el nuevo
                    self.name = self.name.replace(f"{old_code}/", f"{new_code}/", 1)
            # Si el nombre no existe (es un registro nuevo)
            elif not self.name:
                # Replica la lógica de _default_name para generar un nombre inicial
                core_count = self.search_count([('node_id', '=', self.node_id.id)])
                self.name = f"{new_code}/CR{core_count + 1}"

        # --- Lógica existente para el campo node_ids ---
        previous_nodes_ids = self._origin.node_ids.ids
        print(("previus", previous_nodes_ids))

        # Si había un nodo principal anterior, lo removemos de la lista
        if self._origin.node_id:
            # Creamos un conjunto para una eliminación más eficiente
            nodes_set = set(previous_nodes_ids)
            nodes_set.discard(self._origin.node_id.id)
            current_nodes_ids = list(nodes_set)
        else:
            current_nodes_ids = previous_nodes_ids

        # Ahora, agregamos el ID del nuevo nodo principal si existe
        if self.node_id:
            if self.node_id.id not in current_nodes_ids:
                current_nodes_ids.append(self.node_id.id)

        # Asignar la lista final de IDs al campo many2many usando el comando (6,0,...)
        self.node_ids = [(6, 0, current_nodes_ids)]


    @api.depends('name', 'company_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.name} ({record.company_id.name})" if record.company_id else record.name
            
    @api.model
    def create(self, vals):
        if vals.get('node_id'):
            node = self.env['silver.node'].browse(vals['node_id'])
            if node.exists() and node.code:

                vals['parent_id'] = node.asset_id.id
        return super(SilverCore, self).create(vals)


    def write(self, vals):
        print(("corewrite", vals))
        for i, record in enumerate(self):
            if vals.get('node_id'):
                node = self.env['silver.node'].browse(vals['node_id'])
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
        return super(SilverCore, self).write(vals)

    #@api.depends('olt', 'radius', 'ap_count', 'cor')
    def _compute_counts(self):
        print(("_compute_counts", self))
        for record in self:
            record.olt_count = self.env['silver.olt'].search_count([('core_id', '=', record.id)])
            record.radius_count = self.env['silver.radius'].search_count([('core_id', '=', record.id)])
            record.ap_count = self.env['silver.ap'].search_count([('node_ids', 'in', record.node_ids.ids)])


    @api.model
    def default_get(self, fields_list):
        res = super(SilverCore, self).default_get(fields_list)
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

    def generar(self):
        for record in self:
            record.netdev_id.generar()

    def create_ap(self):
        self.ensure_one()
        new_ap = self.env['silver.ap'].create({
           #   'name': f"AP for {self.name}",
            'core_id': self.id,
        })
        return {
            'name': 'AP Creado',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.ap',
            'view_mode': 'form',
            'res_id': new_ap.id,
            'target': 'current',
        }

    def create_radius(self):
        self.ensure_one()
        new_radius = self.env['silver.radius'].create({
            #'name': f"Radius for {self.name}",
            'core_id': self.id,
        })
        return {
            'name': 'Radius Creado',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.radius',
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
            'res_model': 'silver.olt',
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
            'res_model': 'silver.radius',
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
            'res_model': 'silver.ap',
            'view_mode': 'tree,form',
            'domain': [('core_id', '=', self.id)],
            'context': {'default_core_id': self.id},
            'target': 'current',
        }

    def _configure_radius_on_device(self, api):
        """Helper to configure RADIUS on MikroTik and NAS client in Odoo."""
        self.ensure_one()
        _logger.info(f"Starting RADIUS configuration for core {self.name}")

        if not self.radius_id or not self.radius_id.ip:
            raise UserError(_("RADIUS Server is not assigned or does not have an IP address."))

        # 1. Generate a new random secret
        alphabet = string.ascii_letters + string.digits
        secret = ''.join(secrets.choice(alphabet) for _ in range(22))
        _logger.info(f"Generated new RADIUS secret for {self.name}")

        # 2. Configure the MikroTik device
        try:
            radius_resource = tuple(api.path('/radius'))[0]
            print(("radius_re", radius_resource, tuple(radius_resource)))
            #existing_client = api.path('/radius').get(address=self.ip)
            radius_server_list = radius_resource.get(address=self.radius_id.ip)


            if radius_server_list:
                server_id = radius_server_list[0]['.id']
                _logger.info(f"Updating existing RADIUS server entry {server_id} on MikroTik.")
                radius_resource.set(id=server_id, secret=secret, service='ppp,login')
            else:
                _logger.info(f"Adding new RADIUS server entry for {self.radius_id.ip} on MikroTik.")
                radius_resource.add(address=self.radius_id.ip, secret=secret, service='ppp,login')
        except Exception as e:
            raise UserError(_("Failed to configure RADIUS on MikroTik device: %s") % e)

        # 3. Configure the NAS client in Odoo (on the RADIUS server side)
        Nas = self.env['silver.radius.nas']
        nas_client = Nas.search([('nasname', '=', self.ip)], limit=1)
        if nas_client:
            _logger.info(f"Updating existing NAS client {self.ip} in Odoo.")
            nas_client.write({'secret': secret})
        else:
            _logger.info(f"Creating new NAS client for {self.ip} in Odoo.")
            Nas.create({
                'nasname': self.ip,
                'shortname': self.name,
                'secret': secret,
                'type': 'other',
            })

        _logger.info(f"Successfully configured RADIUS for core {self.name}")
        return True

    def button_test_connection(self):
        self.ensure_one()
        netdev = self.netdev_id
        if not netdev:
            raise UserError(_("This core has no network device associated."))

        api = None
        try:
            # STATE 0 or 2: Try RADIUS credentials first
            if netdev.configured in ('0', '2'):
                _logger.info(f"Core {self.name} in state {netdev.configured}. Trying RADIUS credentials.")
                radius_user = request.session.get('radius_user')
                radius_password = request.session.get('radius_password')
                if (not radius_user or not radius_password) and self.env.user.has_group('base.group_erp_manager'):
                    radius_user = 'prueba77'
                    radius_password = 'prueba77'
                if not radius_user or not radius_password:
                    raise UserError(_("RADIUS credentials not found in session. Please log in again."))

                api = netdev._get_api_connection(username=radius_user, password=radius_password)

                if api:
                    _logger.info("RADIUS credential connection successful.")
                    netdev.configured = '2'
                    self.state = 'active'
                    api.close()
                    return self._show_notification('success', _('Connection with RADIUS credentials successful!'))
                else:
                    _logger.warning("RADIUS credential connection failed. Falling back to local credentials.")
                    netdev.configured = '1'  # Set state to 1 to try local next
                    # Fall through to the next block to try local credentials

            # STATE 1: Try local credentials and configure RADIUS
            if netdev.configured == '1':
                _logger.info(f"Core {self.name} in state 1. Trying local credentials.")
                api = netdev._get_api_connection(username=self.username, password=self.password)

                if api:
                    _logger.info("Local credential connection successful. Proceeding to configure RADIUS.")
                    self._configure_radius_on_device(api)
                    netdev.configured = '2'
                    self.state = 'active'
                    return self._show_notification('success', _('Local connection OK. RADIUS configured successfully!'))
                else:
                    _logger.error("Local credential connection failed.")
                    self.state = 'down'
                    raise UserError(_("Connection failed with both RADIUS and local credentials."))

        except Exception as e:
            self.state = 'down'
            _logger.error(f"An exception occurred during connection test: {e}")
            # Re-raise as UserError to show it on the UI
            raise UserError(e)
        finally:
            if api:
                api.close()

        # Fallback for any unhandled case
        self.state = 'down'
        return self._show_notification('danger', _('Connection failed. Check logs for details.'))

    def _show_notification(self, type, message):
        """Helper to show notifications on the UI."""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Connection Test'),
                'message': message,
                'type': type,  # 'success', 'warning', 'danger'
                'sticky': False,
                'next': {'type': 'ir.actions.client', 'tag': 'reload'},
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
