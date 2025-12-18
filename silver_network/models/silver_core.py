import ipaddress
from odoo import models, fields, api, _
from odoo.http import request
from odoo.exceptions import UserError
from odoo.exceptions import UserError
import logging, string, secrets
import re, html
import librouteros
from librouteros.query import Key

from odoo.exceptions import ValidationError


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


class SilverCore(models.Model):
    _name = 'silver.core'
    #_table = 'isp_core'
    _description = 'Equipo Router'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    askuser = fields.Boolean(string='Pedir usuario')


    name = fields.Char(string='Nombre')

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
    radius_id = fields.Many2one('silver.core', string='Radius Servicios')
    radius_admin_id = fields.Many2one('silver.core', string='Radius Admin')
    networks_device_id = fields.Many2many('silver.device.networks', string='Networks Device')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)

    custom_channel_ids = fields.One2many('address.list.channel.line', 'core_id', string='Canales')
    silver_core_port_line_ids = fields.One2many('silver.core.port.line', 'core_id', string='Líneas Puerto Slot')

    kex_algorithms_ids = fields.Many2many('silver.kex.algorithms', string='Kex Algorithms')

    #vlan_ids = fields.Many2many('silver.vlan', 'silver_mvlan_core', 'core_id', 'vlan_id', string='Vlans')
    vlan_ids = fields.One2many('silver.vlan', 'core_id', string='Vlans')



    pooOnlyCore = fields.Boolean(string='Pool de IPs Único')


    silver_address_id = fields.Many2one('silver.address', string='Dirección')

    radius_client_ip = fields.Char(string='Radius Server IP')
    radius_client_secret = fields.Char(string='Radius Shared Secret')
    radius_client_services = fields.Many2many('silver.radius.service', string='Radius Services') # Assuming a model silver.radius.service exists or will be created


    type_access_net = fields.Selection(
        [('inactive', 'Inactivo'), ('dhcp', 'DHCP Leases'), ('manual', 'IP Asignada manualmente'),
         ('system', 'IP Asiganada por el sistema')], default='inactive', string='Tipo Acceso', required=True)


    dhcp_custom_server = fields.Char(string='DHCP Leases')
    interface = fields.Char(string='Interface')
    is_dhcp_static = fields.Boolean(string='Habilitar Dhcp Static')
    dhcp_client = fields.Boolean(string='Profiles VSOL')



    ip_address_pool_ids = fields.One2many('silver.ip.address.pool', 'core_id', string='Pools de direcciones IP')
    ip_address_ids = fields.One2many('silver.ip.address', related='ip_address_pool_ids.address_ids', string='Direcciones IP')



    # --- Campos de Conectividad y Acceso ---
    user = fields.Char(string='Usuario')
    username = fields.Char(string='Usuario Router', )
    user_nass = fields.Char(string='Usuario Nass')
    password = fields.Char(string='Password', )
    password_nass = fields.Char(string='Password Nass')
    key_pppoe = fields.Char(string='Password PPPoE')

    port = fields.Integer(string='Puerto Mikrotik', readonly=False, default=21000)
    port_coa = fields.Char(string='Puerto COA')
    ip = fields.Char(string='IP de Conexión', readonly=False)


    interface = fields.Char(string='Interface')
    cvlan = fields.Char(string='CVLAN')
    svlan = fields.Char(string='SVLAN')

    # --- Campos de Estado y Métricas (calculados) ---
    #state = fields.Selection([('draft', 'Borrador'), ('active', 'Activo'),  ('down', 'Down')], string='Status')
    state = fields.Selection([('down', 'Down'), ('active', 'Active'), ('pending', 'Probar')],
                           #  related = 'netdev_id.state',
                             string='Estado', default='pending')
    display_name = fields.Char(string='Display Name', compute='_compute_display_name')

    olt_count = fields.Integer(string='Conteo Equipo OLT', compute='_compute_counts')
    radius_count = fields.Integer(string='Conteo Servidor Radius', compute='_compute_counts')
    ap_count = fields.Integer(string='Conteo Equipo AP', compute='_compute_counts')

    olt_ids = fields.Many2many('silver.olt', 'silver_core_olt', 'olt_id', 'core_id', string='Equipos OLT')
    #olt_ids = fields.One2many('silver.olt', 'core_id', string='OLTs')
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
    is_active_vlans = fields.Boolean(string='Activar Vlans Router')

    is_type_core_access = fields.Boolean(string='Acceso', default=True)
    is_type_core_bandwidth = fields.Boolean(string='Ancho de banda')

    is_desactive_core = fields.Boolean(string='Desactivar Router')
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

    retries = fields.Integer(string="Reintentos")


    @api.constrains('ip')
    def _check_valid_ip(self):
        """Valida que la dirección IP sea IPv4 o IPv6 válida."""
        for record in self:
            if record.ip:
                try:
                    # Intenta crear un objeto IPv4 o IPv6. Si falla, lanza ValueError.
                    ipaddress.ip_address(record.ip)
                except ValueError:
                    raise ValidationError(
                        ("La dirección IP '%s' no es válida. Por favor, ingrese un formato IPv4 o IPv6 correcto.")
                        % record.ip
                    )

    @api.onchange('ip')
    def _onchange_direccion_ip(self):
        if self.ip:
            try:
                # Si es inválida, forzamos un UserError (lo convierte en un Warning)
                ipaddress.ip_address(self.ip)
            except ValueError:
                self.env['bus.bus']._sendone(
                    # El canal es el usuario actual, por lo que solo él la verá
                    self.env.user.partner_id,

                    'simple_notification',  # Tipo de notificación

                    {
                        'type': 'danger',  # Rojo para error
                        'title': 'Error de Formato IP',
                        'message': f"La dirección '{self.ip}' no es una IP válida. ¡Hay que corregirla!",
                        'sticky': False,  # Para que no se quite sola
                    }
                )

        # @api.onchange('node_id')




    @api.onchange('node_id')
    def _compute_hostname(self):
        print(('h1', self))

        core = self

        if not core.node_id:
            core.name = ''
            return

        cores = self.env['silver.core'].search([('node_id', '=', core.node_id.id)])
        i = 1
        for o in cores:
            if o.name:
                patron = r'(\d+)$'
                match = re.search(patron, o.name)
                print(("re", match, i, o))
                if not match: continue
                if (core._origin.id == o.id): continue
                on = int(match.group(1))
                print(("on", on, o.id, core.id, o.id == core.id, core._origin.id == o.id))
                if on >= i: i = on + 1

        name = f"{core.node_id.code}/CR{i}"

        # Construimos el código.
        # Si el campo 'code' del nodo es 'u', y ya tiene 2 cores, el nuevo será 'u/2'
        core.name = name
        print(("h3", core.name))

    def _onchange_node_id(self):
        # --- Actualización del nombre en tiempo real ---


        patron_regex = r"^(.+)/CR(\d+)$"
        if self.node_id:
            if (not self.name) or (not  len(self.name)) or re.match(patron_regex, self.name):
                new_code = self.node_id.code
                core_count = self.search_count([('node_id', '=', self.node_id.id)])
                self.name = f"{new_code}/CR{core_count + 1}"


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


    @api.depends('name', 'hostname_core', 'company_id')
    def _compute_display_name(self):
        for record in self:
            if record.hostname_core:
                record.display_name = record.hostname_core
            else:
                record.display_name = f"{record.name} ({record.company_id.name})" if record.company_id else record.name
            
    @api.model
    def create(self, vals):
        #if vals.get('node_id'):
          #  node = self.env['silver.node'].browse(vals['node_id'])
           # if node.exists() and node.code:

           #     vals['parent_id'] = node.asset_id.id
        return super(SilverCore, self).create(vals)


    #@api.model
    #def rwrite(self, vals):
    #    if 'core_id' in vals:
    #        new_core = self.env['silver.core'].browse(vals['core_id'])
    #        if new_core.exists():
    #            for record in self:
    #                radius_count = self.search_count([('core_id', '=', new_core.id)])
    #                record.name = f"{new_core.name}/RADIUS{radius_count + 1}"
    #    return super(SilverRadius, self).write(vals)


    def write(self, vals):
        print(("corewrite"))
        if ('name' in vals):
            l = len(self.name) + 1
          #  for olt in self.olt_ids:
          #      print(("olt", olt.name[:l], self.name + "/"))
          #      if olt.name[:l] == self.name + "/":
          #          print(("wr", ({"name": vals['name'] + "/" + olt.name[l:]})))
          #          olt.write({"name": vals['name'] + "/" + olt.name[l:]})

            for ap in self.ap_ids:
                print(("ap", ap.name[:l], self.name + "/"))
                if ap.name[:l] == self.name + "/":
                    print(("wr", ({"name": vals['name'] + "/" + ap.name[l:]})))
                    ap.write({"name": vals['name'] + "/" + ap.name[l:]})


        return super().write(vals)

    #@api.depends('olt', 'radius', 'ap_count', 'cor')
    def _compute_counts(self):
        print(("_compute_counts", self))
        for record in self:
            record.olt_count = self.env['silver.olt'].search_count([('core_id', '=', record.id)])
            record.radius_count = self.env['silver.core'].search_count([('core_id', '=', record.id)])
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
            for ret in record.ip_address_pool_ids:
                print(("ret", ret))
                ret.action_generate_ips()


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

    def action_create_and_link_ap(self):
        self.ensure_one()
        return {
            'name': _('Crear AP'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.ap',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_core_id': self.id,
            }
        }

    def action_open_aps_to_link(self):
        self.ensure_one()
        unassigned_aps_count = self.env['silver.ap'].search_count([('core_id', '=', False)])
        if unassigned_aps_count == 0:

            raise UserError(_('No hay APs sin asignar.'))

        return {
            'name': 'Agregar AP',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.core.link.ap.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_create_and_link_olt(self):
        self.ensure_one()
        return {
            'name': _('Crear OLT'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.olt',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_core_id': self.id,
            }
        }

    def action_open_olts_to_link(self):
        self.ensure_one()
        unassigned_olts_count = self.env['silver.olt'].search_count([('core_id', '=', False)])
        if unassigned_olts_count == 0:
           # return
            raise UserError(_('No hay OLTs sin asignar.'))

        return {
            'name': 'Agregar OLT',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.core.link.olt.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def create_radius(self):
        self.ensure_one()
        new_radius = self.env['silver.core'].create({
            #'name': f"Radius for {self.name}",
            'core_id': self.id,
            'is_radius': True
        })
        return {
            'name': 'Radius Creado',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.core',
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
                'title': 'Crear NAS',
                'message': 'NAS creado',
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
                'title': 'Quitar NAS',
                'message': 'NAS quitado',
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
                'message': 'Connection to Router was successful!',
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
            'res_model': 'silver.core',
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



    def action_view_form(self):
        self.ensure_one()
        return {
            'name': _('Router'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.core',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    def _get_api_connection(self, username=None, password=None):
        self.ensure_one()
        p = self.port# or self.api_port

        # Use provided credentials, fallback to self, then to session
        user_to_try = username or self.username or request.session.get('radius_user')
        pass_to_try = password or self.password or request.session.get('radius_password')

        print(("getapi", user_to_try, pass_to_try, self.id))

        if not user_to_try or not pass_to_try:
            #self.write({'state': 'error'})
            self.state = 'down'

            _logger.error("Connection attempt failed: No username or password provided.")
            return (None, 'No usuario o contraseña')

        try:
           # self.state = 'connecting'
           # self.write({'state': 'connecting'})
            _logger.info(f"Attempting to connect to {self.ip}:{p} with user '{user_to_try}'")
            api = librouteros.connect(
                host=self.ip,
                username=user_to_try,
                password=pass_to_try,
                port=int(p),
                encoding='latin-1'
            )
            _logger.info(f"Successfully connected to {self.ip}")
            #self.write({'state': 'connected'})
            self.state = 'active'
            return (api, None)
        except Exception as e:
            _logger.error(f"Failed to connect to {self.ip}:{p} with user '{user_to_try}'. Error: {e}")
            self.state = 'down'
            #self.write({'state': 'error'})
            return (None, f"{e}")

    def _configure_radius_on_device(self, core_api):
        """
        Configures the RADIUS client on the Core device and
        registers the Core as a NAS client on the RADIUS server.
        """
        self.ensure_one()
        _logger.info(f"Starting full RADIUS configuration for Router {self.name}")

        radius_id = (self if self.is_radius else self.radius_id)

        if not radius_id or not radius_id.ip:
            raise UserError(_("RADIUS Server is not assigned or does not have an IP address."))

        if self.radius_client_secret:
            secret = self.radius_client_secret
        else:
            alphabet = string.ascii_letters + string.digits
            secret = ''.join(secrets.choice(alphabet) for _ in range(22))
            self.radius_client_secret = secret


        # 1. Get or create the NAS secret and Odoo record
        """Nas = self.env['silver.radius.nas']
        nas_client = Nas.search([('nasname', '=', self.ip)], limit=1)
        if nas_client and nas_client.secret:
            secret = nas_client.secret
            _logger.info(f"Found existing NAS secret for {self.ip} in Odoo.")
        else:
            alphabet = string.ascii_letters + string.digits
            secret = ''.join(secrets.choice(alphabet) for _ in range(22))
            _logger.info(f"Generated new RADIUS secret for {self.name}")
            if nas_client:
                nas_client.write({'secret': secret})
            else:
                Nas.create({
                    'nasname': self.ip,
                    'shortname': self.name,
                    'secret': secret,
                    'type': 'other',
                })
            _logger.info(f"Saved NAS client for {self.ip} in Odoo.")
"""

        # 2. Configure the MikroTik Core device to use the RADIUS server
        try:
            radius_resource = core_api.path('/radius')
            # Find if a radius server for 'login' service is already configured
            for s in radius_resource:
                print(("s",s))
            existing_server = next((s for s in radius_resource if s.get('service') == 'login'), None)

            params = {
                'secret': secret,
                'service': 'login',
                'address': radius_id.ip,
                'src-address': self.ip,
            }
            print(("existing", existing_server))


            if existing_server:
                server_id = existing_server['.id']
                _logger.info(f"Updating existing RADIUS server entry {server_id} on Router device.")
            #    radius_resource.update(numbers=server_id, **params)
            else:
                _logger.info(f"Adding new RADIUS server entry for {radius_id.ip} on Router device.")
             #   radius_resource.add(**params)
        except Exception as e:
            raise UserError(_("Failed to configure RADIUS on Router device: %s") % e)

        # 3. Configure the RADIUS server to accept the Core as a NAS client
        radius_api = None
        try:
            _logger.info(f"Connecting to RADIUS server {radius_id.name} at {radius_id.ip} to configure NAS.")
            radius_api,e = radius_id._get_api_connection()
            if not radius_api:
                raise UserError(_("Could not connect to the RADIUS server: %s")%f"{e}")

            # In MikroTik User Manager, NAS clients are called "routers"
            nas_resource = radius_api.path('/user-manager/router')
            existing_nas = next((n for n in nas_resource if n.get('ip-address') == self.ip), None)

            nas_params = {
                'ip-address': self.ip,
                'shared-secret': secret,
                'name':self.hostname_core,
                "coa-port":3799
            }

            if existing_nas:
                nas_id = existing_nas['.id']
                _logger.info(f"Updating existing NAS client {self.ip} on RADIUS server's User Manager.")
            #    nas_resource.update(numbers=nas_id, **nas_params)
            else:
                _logger.info(f"Adding new NAS client for {self.ip} to RADIUS server's User Manager.")
            #    nas_resource.add(**nas_params)

        except Exception as e:
            raise UserError(_("Failed to configure NAS on RADIUS server: %s") % e)
        finally:
            if radius_api:
                radius_api.close()

        _logger.info(f"Successfully configured RADIUS for Router {self.name}")
        return True



    def check_and_configure_nas(self, username, password):
        """
        Punto de entrada público para verificar y configurar el Core como un cliente NAS en el RADIUS.
        """
        self.ensure_one()


        radius_id = (self if self.is_radius else self.radius_id)
        api = None
        try:
            # Conectar al dispositivo Core usando las credenciales locales
            _logger.info(f"Iniciando configuración NAS para {self.name} en el RADIUS {radius_id.name} con user {username}")
            api,e = self._get_api_connection(username=username, password=password)
            if not api:
                print(("notapi", e))
                return False
                #raise UserError(_("No se pudo conectar al dispositivo Core para la configuración NAS."))

            # Llamar a la lógica de configuración existente
            self._configure_radius_on_device(api)

            _logger.info(f"Configuración NAS para {self.name} completada exitosamente.")
            return True #self._show_notification('success', _('El cliente NAS fue configurado exitosamente en el servidor RADIUS.'))

        except Exception as e:
            _logger.error(f"Fallo durante la configuración NAS para {self.name}: {e}")
            # Re-lanza la excepción para que sea visible en la UI.
            raise False #UserError(_("Fallo en la configuración NAS: %s") % e)
        finally:
            if api:
                api.close()




    def action_unlink_from_node(self):
        self.ensure_one()
        self.write({'node_id': False})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def button_test_connection(self):
        self.ensure_one()

        print(("test connection", self.env.context))

        
        api = None
        ostate = self.state
        try:

            # Connection test now requires local credentials to perform configuration
            _logger.info(f"Router {self.name}: Trying local credentials for connection and configuration.")
            if self.env.context.get('u'):
                api,e = self._get_api_connection(username=self.username, password=self.password)
            else:
                api,e = self._get_api_connection()

            print(("noapi", self.state, ostate, api, e))
            cambia = False

            if api:
                # Fetch and set the hostname first
                _logger.info("Fetching system identity from Router device.")
                identity_resource = tuple(api.path('/system/identity'))
                if identity_resource and self.hostname_core != identity_resource[0].get('name'):
                    cambia = True
                    hostname = identity_resource[0].get('name')
                    if hostname:
                        _logger.info(f"Found hostname: {hostname}. Updating record.")
                        #self.write({'hostname_core': hostname})
                        self.hostname_core = hostname



                _logger.info("Local credential connection successful. Proceeding to configure RADIUS.")
                if self.env.context.get('u'):
                    self._configure_radius_on_device(api)

                cambia = cambia or (ostate != 'active')
                self.askuser = False
                self.state = 'active'
                self.retries = 0
            #    return self._show_notification('success', _('RADIUS and NAS ya configurados'))

                if (cambia):
                    return True


                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Éxito',
                        'sticky': False,
                        'message': 'Conexión al Router  exitosa!',
                        'type': 'success',
           #             'next': reload_action,
                    }
                }
            #else:
            _logger.error("Local credential connection failed.")
            #with self.env.registry.cursor() as new_cr:
            cambia = (ostate != 'down') or (self.retries == 3)
            if (self.state != 'down'):
                self.state = 'down'
            if "auth" in f"{e}" or "username" in f"{e}" or "usuario" in f"{e}":
                self.askuser = True
                cambia = True
            self.retries = self.retries + 1
            #new_cr.commit()

            if cambia :
                return True

            r = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'sticky': False,
                    'message': f'Conexión al Router fallida: {e}',
                    'type': 'danger',
            #        'next': reload_action,
                }
            }
            print(("test connectionn", r))
            return r

            #    return self._show_notification('danger', _('Radius no conectado, ingrese usuario y contraseña locales'))
                #raise UserError(_("Radius no conectado, ingrese usuario y contraseña locales"))

        except Exception as e:
            print("exepsion")
            cambia = (ostate != 'down')
            self.state = 'down'
            _logger.error(f"An exception occurred during connection test: {e}")
            if (cambia): return True
            # Re-raise as UserError to show it on the UI
            #raise UserError(e)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'sticky': False,
                    'message': f'Exception en Router: {e}',
                    'type': 'danger',
           #         'next': reload_action,
                }
            }
        finally:
            if api:
                api.close()

    def create_user_manager_user(self, username, password, customer='admin', ip_address=None, rate_limit=None):
        """
        Crea o actualiza un usuario en MikroTik User Manager con atributos RADIUS.

        :param username: El nombre de usuario a crear/actualizar.
        :param password: La contraseña para el usuario.
        :param customer: El cliente/propietario del usuario (default: 'admin').
        :param ip_address: La dirección IP estática para asignar (Framed-IP-Address).
        :param rate_limit: El límite de velocidad (Mikrotik-Rate-Limit).
        :return: dict con {'success': bool, 'message': str}
        """
        self.ensure_one()
        api = self._get_mikrotik_api()
        try:
            _logger.info(f"Procesando usuario '{username}' en User Manager de {self.ip}")
            user_path = api.path('/user-manager/user')
            name_key = Key("name")

            # --- Datos base del usuario ---
            user_data = {
                'name': username,
                'password': password,
                'comment': customer,
                'shared-users': '1',
            }

            # 1. Verificar si el usuario ya existe y crearlo o actualizarlo
            existing_user = tuple(user_path.select(Key(".id")).where(name_key == username))
            user_id = None
            if existing_user:
                user_id = existing_user[0]['.id']
                user_data['.id'] = user_id
                user_path.update(**user_data)
                message = f"Usuario '{username}' actualizado. "
            else:
                # .id no es un parámetro válido para 'add', así que lo eliminamos si existe
                user_data.pop('.id', None)
                new_user = user_path.add(**user_data)
                # The API returns a tuple, we need the '.id' from the first element
                # user_id = new_user[0]['.id']
                user_id = tuple(api.path('/user-manager/user').select(Key('.id')).where(name_key == username))[0]['.id']
                message = f"Usuario '{username}' creado. "

            # 2. Construir y aplicar los atributos RADIUS
            attributes = {}
            if ip_address:
                attributes['Framed-IP-Address'] = ip_address
            if rate_limit:
                attributes['Mikrotik-Rate-Limit'] = rate_limit

            if attributes:
                # CORRECCIÓN: Pasar los atributos como una LISTA de strings, no un solo string.
                attribute_str = ",".join([f"{key}:{value}" for key, value in attributes.items()])

                # Aplicar los atributos al usuario usando su ID
                user_path.update(**{
                    '.id': user_id,
                    'group': 'Cliente',
                    'attributes': attribute_str
                })
                message += "Atributos RADIUS aplicados."

            _logger.info(message)
            return {'success': True, 'message': message}

        except Exception as e:
            error_message = f"Fallo al procesar el usuario '{username}' en User Manager: {e}"
            _logger.error(error_message)
            return {'success': False, 'message': error_message}
        finally:
            if api:
                api.close()

    def button_add_update_radius_client(self):
        self.ensure_one()
        if not self.ip:  # or not self.radius_client_secret:
            raise UserError(("Radius Server IP and Shared Secret are required."))

        api,e = self._get_api_connection()
        if api:
            try:
                # Check if Radius client for this IP already exists
                r = api.path('/radius')
                print(("radius", r, dir(r), api.path('/radius')))
                existing_client = api.path('/radius').get(address=self.ip)
                # tuple(api.path('/system/resource'))[0]

                services_str = ",".join(
                    self.radius_client_services.mapped('name')) if self.radius_client_services else ""

                if existing_client:
                    # Update existing client
                    api.path('/radius').set(
                        **{'.id': existing_client[0]['.id'],
                           'secret': self.radius_client_secret,
                           'service': services_str,
                           'authentication': 'yes',
                           'accounting': 'yes'}
                    )
                    message = "Radius client updated successfully!"
                else:
                    # Add new client
                    api.path('/radius').add(
                        address=self.ip,
                        secret=self.radius_client_secret,
                        service=services_str,
                        authentication='yes',
                        accounting='yes'
                    )
                    message = "Radius client added successfully!"

                self.write({'state': 'active'})
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': message,
                        'type': 'success',
                    }
                }
            except Exception as e:
                self.write({'state': 'error'})
                raise UserError(("Failed to configure Radius client: %s") % e)
            finally:
                api.close()
        else:
            raise UserError(_("Could not connect to the MikroTik router: %s")%f"{e}")

    def button_remove_radius_client(self):
        self.ensure_one()
        if not self.radius_client_ip:
            raise UserError(_("Radius Server IP is required to remove the client."))

        api,e = self._get_api_connection()
        if api:
            try:
                existing_client = api.path('/radius').get(address=self.radius_client_ip)
                if existing_client:
                    api.path('/radius').remove(id=existing_client[0]['.id'])
                    message = "Radius client removed successfully!"
                else:
                    message = "Radius client not found for this IP."

                self.write({'state': 'active'})
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': message,
                        'type': 'success',
                    }
                }
            except Exception as e:
                self.write({'state': 'error'})
                raise UserError(_("Failed to remove Radius client: %s") % e)
            finally:
                api.close()
        else:
            raise UserError(_("Could not connect to the MikroTik router:%s")%f"{e}")

    def button_get_system_info(self):
        self.ensure_one()
        api,e = self._get_api_connection()
        if not api:
            raise UserError(_("Could not connect to the device: %s")%f"{e}")

        info_str = ""
        try:
            # Get System Resource
            resource = tuple(api.path('/system/resource'))
            if resource:
                info_str += "--- System Resources ---\n"
                for key, value in resource[0].items():
                    info_str += f"{key.replace('-', ' ').title()}: {value}\n"
                info_str += "\n"

            # Get System Health
            health = tuple(api.path('/system/health'))
            if health:
                info_str += "--- System Health ---\n"
                for key, value in health[0].items():
                    info_str += f"{key.replace('-', ' ').title()}: {value}\n"
                info_str += "\n"

            # Get RouterBoard Info
            routerboard = tuple(api.path('/system/routerboard'))
            if routerboard:
                info_str += "--- RouterBoard ---\n"
                for key, value in routerboard[0].items():
                    info_str += f"{key.replace('-', ' ').title()}: {value}\n"

            wizard = self.env['silver.netdev.system.info.wizard'].create({
                'info': info_str,
                'netdev_id': self.id
            })

            return {
                'name': 'System Information',
                'type': 'ir.actions.act_window',
                'res_model': 'silver.netdev.system.info.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
            }

        except Exception as e:
            raise UserError(_("Failed to fetch system info: %s") % e)
        finally:
            api.close()

    def button_view_interfaces(self):
        self.ensure_one()
        api,e = self._get_api_connection()
        if not api:
            return UserError(_("Failed to fetch system interfaces: %s") % e)

        try:
            wizard = self.env['silver.netdev.interface.wizard'].create({
                'netdev_id': self.id
            })

            # Helper function to create records to avoid repetition
            def create_lines(model_name, data, mapping, traffic_map):
                model = self.env[model_name]
                for item in data:
                    vals = {'wizard_id': wizard.id}
                    for odoo_field, mikrotik_field in mapping.items():
                        vals[odoo_field] = item.get(mikrotik_field)

                    # Add traffic data by looking up the interface name
                    name = item.get('name')
                    if name in traffic_map:
                        traffic = traffic_map[name]
                        vals['rx_speed'] = _format_speed(traffic.get('rx-bits-per-second', 0))
                        vals['tx_speed'] = _format_speed(traffic.get('tx-bits-per-second', 0))

                    model.create(vals)

            # 1. General Interfaces (Main Tab)
            interfaces = tuple(api.path('/interface'))
            interface_names = [iface.get('name') for iface in interfaces]

            # MikroTik's monitor-traffic has a limit on the number of interfaces.
            # We process them in chunks to avoid the error.
            traffic_map = {}
            chunk_size = 90  # A safe limit below 100
            for i in range(0, len(interface_names), chunk_size):
                chunk = interface_names[i:i + chunk_size]
                traffic_chunk_data = api.path('/interface')('monitor-traffic', interface=",".join(chunk), once='')
                for item in traffic_chunk_data:
                    traffic_map[item['name']] = item

            for interface in interfaces:
                name = interface.get('name')
                traffic = traffic_map.get(name, {})
                self.env['silver.netdev.interface.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'name': name,
                    'mac_address': interface.get('mac-address'),
                    'type': interface.get('type'),
                    'running': interface.get('running'),
                    'disabled': interface.get('disabled'),
                    'comment': interface.get('comment'),
                    'rx_speed': _format_speed(traffic.get('rx-bits-per-second', 0)),
                    'tx_speed': _format_speed(traffic.get('tx-bits-per-second', 0)),
                })

            # 2. Ethernet
            ethernet_data = tuple(api.path('/interface/ethernet'))
            create_lines('silver.netdev.interface.ethernet.line', ethernet_data, {
                'name': 'name', 'mac_address': 'mac-address', 'mtu': 'mtu',
                'l2mtu': 'l2mtu', 'arp': 'arp', 'disabled': 'disabled', 'comment': 'comment'
            }, traffic_map)

            # 3. EoIP Tunnels
            eoip_data = tuple(api.path('/interface/eoip'))
            create_lines('silver.netdev.interface.eoip.line', eoip_data, {
                'name': 'name', 'remote_address': 'remote-address', 'tunnel_id': 'tunnel-id',
                'mac_address': 'mac-address', 'mtu': 'mtu', 'disabled': 'disabled', 'comment': 'comment'
            }, traffic_map)

            # 4. GRE Tunnels
            gre_data = tuple(api.path('/interface/gre'))
            create_lines('silver.netdev.interface.gre.line', gre_data, {
                'name': 'name', 'remote_address': 'remote-address', 'local_address': 'local-address',
                'mtu': 'mtu', 'disabled': 'disabled', 'comment': 'comment'
            }, traffic_map)

            # 5. VLANs
            vlan_data = tuple(api.path('/interface/vlan'))
            create_lines('silver.netdev.interface.vlan.line', vlan_data, {
                'name': 'name', 'vlan': 'vlan-id', 'interface': 'interface',
                'mtu': 'mtu', 'arp': 'arp', 'disabled': 'disabled', 'comment': 'comment'
            }, traffic_map)

            # 6. VRRP
            vrrp_data = tuple(api.path('/interface/vrrp'))
            create_lines('silver.netdev.interface.vrrp.line', vrrp_data, {
                'name': 'name', 'interface': 'interface', 'vrid': 'vrid', 'priority': 'priority',
                'interval': 'interval', 'disabled': 'disabled', 'comment': 'comment'
            }, traffic_map)

            # 7. Bonding
            bonding_data = tuple(api.path('/interface/bonding'))
            create_lines('silver.netdev.interface.bonding.line', bonding_data, {
                'name': 'name', 'slaves': 'slaves', 'mode': 'mode',
                'link_monitoring': 'link-monitoring', 'mtu': 'mtu', 'disabled': 'disabled', 'comment': 'comment'
            }, traffic_map)

            # 8. LTE
            lte_data = tuple(api.path('/interface/lte'))
            create_lines('silver.netdev.interface.lte.line', lte_data, {
                'name': 'name', 'mac_address': 'mac-address', 'mtu': 'mtu',
                'imei': 'imei', 'pin': 'pin-status', 'disabled': 'disabled', 'comment': 'comment'
            }, traffic_map)

            return {
                'name': 'Router Interfaces',
                'type': 'ir.actions.act_window',
                'res_model': 'silver.netdev.interface.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('silver_network.view_silver_router_interface_wizard_form').id,
                'res_id': wizard.id,
                'target': 'new',
                'context': {
                    'default_netdev_id': self.id,
                }
            }
        finally:
            api.close()


    def button_view_routes(self):
        self.ensure_one()
        api,e = self._get_api_connection()
        if not api:
            return UserError(_("Failed to fetch system routes: %s") % e)

        try:
            routes = tuple(api.path('/ip/route'))
            wizard = self.env['silver.netdev.route.wizard'].create({'router_id': self.id})
            for route in routes:
                self.env['silver.netdev.route.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'dst_address': route.get('dst-address'),
                    'gateway': route.get('gateway'),
                    'distance': route.get('distance'),
                    'active': route.get('active'),
                    'static': route.get('static'),
                    'comment': route.get('comment'),
                })

            return {
                'name': 'Router Routes',
                'type': 'ir.actions.act_window',
                'res_model': 'silver.netdev.route.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
            }
        finally:
            api.close()

    #@api.model
    def button_view_ppp_active(self):
        self.ensure_one()
        api, e = self._get_api_connection()
        if not api:
            return UserError(_("Failed to fetch ppp: %s") % e)

        try:
            ppp_active = tuple(api.path('/ppp/active'))
            wizard = self.env['silver.netdev.ppp.active.wizard'].create({'router_id': self.id})
            for ppp in ppp_active:
                self.env['silver.netdev.ppp.active.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'name': ppp.get('name'),
                    'service': ppp.get('service'),
                    'caller_id': ppp.get('caller-id'),
                    'address': ppp.get('address'),
                    'uptime': ppp.get('uptime'),
                })

            return {
                'name': 'PPP Active Connections1',
                'type': 'ir.actions.act_window',
                'res_model': 'silver.netdev.ppp.active.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
                'context': {
                    'default_netdev_id': self.id,
                }
            }
        finally:
            api.close()


    def button_view_firewall_rules(self):
        self.ensure_one()
        api,e = self._get_api_connection()
        if not api:
            return UserError(_("Failed to fetch firewall: %s") % e)

        try:
            firewall_rules = tuple(api.path('/ip/firewall/filter'))
            wizard = self.env['silver.netdev.firewall.wizard'].create({'router_id': self.id})
            for rule in firewall_rules:
                self.env['silver.netdev.firewall.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'chain': rule.get('chain'),
                    'action': rule.get('action'),
                    'src_address': rule.get('src-address'),
                    'dst_address': rule.get('dst-address'),
                    'protocol': rule.get('protocol'),
                    'comment': rule.get('comment'),
                    'disabled': rule.get('disabled'),
                })

            return {
                'name': 'Firewall Rules',
                'type': 'ir.actions.act_window',
                'res_model': 'silver.netdev.firewall.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
            }
        finally:
            api.close()

    def button_view_queues(self):
        self.ensure_one()
        api,e = self._get_api_connection()
        if not api:
            return UserError(_("Failed to fetch queues: %s") % e)

        try:
            queues = tuple(api.path('/queue/simple'))
            wizard = self.env['silver.netdev.queue.wizard'].create({'router_id': self.id})
            for queue in queues:
                self.env['silver.netdev.queue.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'name': queue.get('name'),
                    'target': queue.get('target'),
                    'max_limit': queue.get('max-limit'),
                    'burst_limit': queue.get('burst-limit'),
                    'disabled': queue.get('disabled'),
                    'comment': queue.get('comment'),
                })

            return {
                'name': 'Queues',
                'type': 'ir.actions.act_window',
                'res_model': 'silver.netdev.queue.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
                'context': {
                    'default_netdev_id': self.id,
                }
            }
        finally:
            api.close()

    def button_view_active_users(self):
        self.ensure_one()
        api, e = self._get_api_connection()
        if not api:
            return UserError(_("Failed to fetch system info: %s") % e)

        try:
            active_users = tuple(api.path('/user/active'))
            wizard = self.env['silver.netdev.active.users.wizard'].create({})

            for user in active_users:
                self.env['silver.netdev.active.users.wizard.line'].create({
                    'wizard_id': wizard.id,
                    'name': user.get('name'),
                    'address': user.get('address'),
                    'via': user.get('via'),
                    'uptime': user.get('uptime'),
                })

            return {
                'name': 'Active Users',
                'type': 'ir.actions.act_window',
                'res_model': 'silver.netdev.active.users.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
            }
        finally:
            if api:
                api.close()


    def action_open_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'silver.core',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    open_form_link = fields.Html(string="Línea", compute="_compute_open_form_link", readonly=True)

    def _compute_open_form_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for line in self:
            if not line.id:
                line.open_form_link = ""
                continue
            url = f"{base_url}/web#id={line.id}&model={line._name}&view_type=form"
            # Aquí pones el campo que quieres que sea el texto del enlace
            text = line.name or line.product_id.display_name or f"Línea {line.sequence}"
            line.open_form_link = f'''<a href='{url}' target="current" >{html.escape(text)}</a>'''

