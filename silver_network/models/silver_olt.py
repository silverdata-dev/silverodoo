import ipaddress
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging, re
from ..models.olt_connection import OLTConnection


_logger = logging.getLogger(__name__)



class SilverOlt(models.Model):
    _name = 'silver.olt'
    _description = 'Equipo OLT'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name_sequence = 'silver.olt.sequence'
    #_table = 'isp_olt'




    hostname_olt = fields.Char(string='Hostname')
    name = fields.Char('Nombre')



    core_ids = fields.Many2many('silver.core', string='Equipos Core')
    core_id = fields.Many2one('silver.core', string='Equipo Core', required=1)
    node_id = fields.Many2one('silver.node', string='Nodo', required=1)
    num_slot_olt = fields.Integer(string='Numero de Slots', default=1)
    num_ports1 = fields.Selection([
        ('1', '1 Puerto'),
        ('4', '4 Puertos'),
        ('8', '8 Puertos'),
        ('16', '16 Puertos'),
        ('32', '32 Puertos'),
        ('64', '64 Puertos'),
    ], string='Slot 0',

        default="8")
    num_ports2 = fields.Selection([
        ('1', '1 Puerto'),
        ('4', '4 Puertos'),
        ('8', '8 Puertos'),
        ('16', '16 Puertos'),
        ('32', '32 Puertos'),
        ('64', '64 Puertos'),
    ], string='Slot 1', default="8")
    num_ports3 = fields.Selection([
        ('1', '1 Puerto'),
        ('4', '4 Puertos'),
        ('8', '8 Puertos'),
        ('16', '16 Puertos'),
        ('32', '32 Puertos'),
        ('64', '64 Puertos'),
    ], string='Slot 2', default="8")
    num_ports4 = fields.Selection([
        ('1', '1 Puerto'),
        ('4', '4 Puertos'),
        ('8', '8 Puertos'),
        ('16', '16 Puertos'),
        ('32', '32 Puertos'),
        ('64', '64 Puertos'),
    ], string='Slot 3', default="8")
    num_ports5 = fields.Selection([
        ('1', '1 Puerto'),
        ('4', '4 Puertos'),
        ('8', '8 Puertos'),
        ('16', '16 Puertos'),
        ('32', '32 Puertos'),
        ('64', '64 Puertos'),
    ], string='Slot 4', default="8")

    kex_algorithms_ids = fields.Many2many('silver.kex.algorithms', string='Kex Algorithms')
    is_multi_user_olt = fields.Boolean(string='Multiples Usuarios')

    secret_olt = fields.Char(string='Secret')
    is_pppoe = fields.Boolean(string='PPPoE')

    g_name_service = fields.Char(string='Name Service')

    tcont = fields.Char(string='Tcont', default=1)
    gemport = fields.Char(string='Gemport', default=1, required=True)

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
    dhcp_custom_server = fields.Char(string='DHCP Leases')
    traffic_table = fields.Selection([('name', 'Name'), ('index', 'Index')], string='Traffic-Table(command)')

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
    profile_dba_internet = fields.Char(string='Profile DBA de Internet', default='max-band')
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
    #vlan_id = fields.Char(string='VLAN ID', required=True)
    #vlan_id = fields.Many2one('silver.vlan', string='VLAN')

    vlan_ids = fields.Many2many('silver.vlan', 'silver_mvlan_olt', 'olt_id', 'vlan_id', string= 'Vlans')


    mtu = fields.Char(string='MTU')
    is_enable_nat = fields.Boolean(string='Enable NAT')
    is_disabled_dhcp_pv4 = fields.Boolean(string='Deshabilitar Dhcp IPv6')
    is_control_admin = fields.Boolean(string='Admin Control', default=1)
    admin_user = fields.Char(string='Admin User')
    admin_passwd = fields.Char(string='Admin Password')
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
    #state = fields.Selection([('down', 'Down'), ('active', 'Active')], string='Estado', default='down')
    state = fields.Selection([('down', 'Down'), ('active', 'Active'), ('pending', 'Probar'),
],

                             string='Estado', default='pending')


    ip = fields.Char(string='IP de Conexion')
    port = fields.Integer(string='Puerto de Conexion')
    username = fields.Char(string='Usuario')
    password = fields.Char(string='Password')
    type_connection = fields.Selection([("ssh","SSH"), ("telnet", "Telnet")], string='Tipo de Conexión')
    port_telnet = fields.Char(string='Puerto telnet', default=23)
    port_ssh = fields.Char(string='Puerto ssh', default=22)

    olt_card_count = fields.Integer(string='Conteo Slot OLT', compute='_compute_olt_card_count')
    #contracts_olt_count = fields.Integer(string='Conteo Olts', compute='_compute_contracts_olt_count')
    ip_range_count = fields.Integer(string='IP Ranges', compute='_compute_ip_range_count')
    isp_tr_069_id = fields.Many2one("isp.tr.069", string="Equipo OLT")

#    "ip_address_line_tr69_ids", "Direcciones IP", "Equipo OLT", "one2many", "Campo base", "", "True", "", "isp.ip.address.line"

    olt_card_port_count = fields.Integer(string='Conteo Puertos', compute='_compute_counts')

    pending_changes = fields.Boolean(string="Cambios Pendientes", default=False, readonly=True, copy=False,
                                     help="Indica si hay cambios en los campos monitoreados que no se han sincronizado con las ONUs.")

    port_ids = fields.One2many('silver.olt.card.port', 'olt_id', string='Puertos')
    card_ids = fields.One2many('silver.olt.card', 'olt_id', string='Tarjetas')



    silver_address_id = fields.Many2one('silver.address', string='Dirección')

    def _compute_olt_card_port_count(self):
        for record in self:
            record.olt_card_port_count = self.env['silver.olt.card.port'].search_count([('olt_id', '=', record.id)])



    ip_address_pool_ids = fields.One2many('silver.ip.address.pool', 'olt_id', string='Pools de direcciones IP')
    ip_address_ids = fields.One2many('silver.ip.address', related='ip_address_pool_ids.address_ids', string='Direcciones IP')


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


    @api.model
    def create(self, vals):
        print(("createee", vals))
       # if vals.get('core_id'):
       #     core = self.env['silver.core'].browse(vals['core_id'])
          #  print(("createee0", core, core.name, core.asset_id, core.asset_id.name))
       #     if core.exists() and core.name and  not vals.get("name"):
       #         olt_count = self.search_count([('core_id', '=', core.id)])
       #         vals['name'] = f"{core.name}/OLT{olt_count + 1}"
       #         print(("createe2e", vals))
        print(("createee3", vals))
        return super(SilverOlt, self).create(vals)


    def write(self, vals):
        print(("apwrite", vals))

        #for i, record in enumerate(self):
        #    if vals.get('coreid'):
        #        core = self.env['silver.core'].browse(vals['core_id'])
        #    else:
        #        core = record.core_id

        #    if core.exists() and core.name:
        #        olt_count = self.search_count([('core_id', '=', core.id)])
        #        vals['name'] = f"{core.name}/OLT{olt_count + 1}"


            # If node_id is set to False, the name is not changed.
        return super(SilverOlt, self).write(vals)



    def action_generar(self):
        self.ensure_one()
        OltCard = self.env['silver.olt.card']
        OltPort = self.env['silver.olt.card.port']

        if self.num_slot_olt > 5:
            self.num_slot_olt = 5
            # Consider raising a UserError or returning a warning to the UI
            raise UserError("El número de slots no puede ser mayor a 5. Se ha ajustado automáticamente a 5.")

        num_ports_per_slot_config = [
            int(self.num_ports1 or 0), int(self.num_ports2 or 0),
            int(self.num_ports3 or 0), int(self.num_ports4 or 0),
            int(self.num_ports5 or 0)
        ]

        # --- Lógica de Borrado ---
        # 1. Borrar puertos sobrantes que no tengan contratos
        all_cards = OltCard.search([('olt_id', '=', self.id)])
        print(("allcards", all_cards))
        for i, card in enumerate(all_cards):

            limit_ports = num_ports_per_slot_config[i]
            if i >= self.num_slot_olt:
                limit_ports = 0
            ports_to_check = OltPort.search([
                ('olt_card_id', '=', card.id),
                ('num_port', '>=', limit_ports)
            ])
            # Filtramos para quedarnos solo con los que no tienen contratos
            ports_to_delete = ports_to_check.filtered(lambda p: not p.contract_ids)
            if ports_to_delete:
                _logger.info(f"Borrando {len(ports_to_delete)} puertos sobrantes de la tarjeta {card.name}")
                ports_to_delete.unlink()

        # 2. Borrar tarjetas sobrantes que no tengan puertos
        cards_to_check = OltCard.search([
            ('olt_id', '=', self.id),
            ('num_card', '>=', self.num_slot_olt)
        ])
        # Filtramos para quedarnos solo con las que no tienen puertos
        cards_to_delete = cards_to_check.filtered(lambda c: not c.port_ids)
        if cards_to_delete:
            _logger.info(f"Borrando {len(cards_to_delete)} tarjetas sobrantes de la OLT {self.name}")
            cards_to_delete.unlink()


        # --- Lógica de Creación (existente) ---
        for i in range(self.num_slot_olt):
            print(("ci", i))
            # Buscar si la tarjeta ya existe
            card = OltCard.search([
                ('olt_id', '=', self.id),
                ('num_card', '=', i)
            ], limit=1)

            print(("cc",card))

            if not card:
                print(("create card", self.name))
                # Crear si no existe

                card = OltCard.create({
                    'name': f'{self.name}/C{i}',
                    'olt_id': self.id,
                    'num_card': i,
                })

            # --- Creación de Puertos (si no existen) ---
            target_port_count = num_ports_per_slot_config[i]
            for j in range(target_port_count):
                port_num = j + 1
                # Buscar si el puerto ya existe en esta tarjeta
                port_exists = OltPort.search([
                    ('olt_card_id', '=', card.id),
                    ('num_port', '=', port_num)
                ], limit=1)

                if not port_exists:
                    # Crear si no existe
                    print(("create port", card.name))
                    OltPort.create({

                        'name': f'{card.name}/P{port_num}',
                        'olt_id': self.id,
                        'olt_card_id': card.id,
                        'olt_card_n': i,
                        'num_port': port_num,
                    })
        
        # Opcional: Notificar al usuario que el proceso terminó
        reload_action = {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
        return [{
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Éxito'),
                'message': _('Estructura de tarjetas y puertos actualizada correctamente.'),
                'type': 'success',
            }
        }, reload_action]


    def action_unlink_from_node(self):
        self.ensure_one()
        self.write({'node_id': False})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_unlink_from_core(self):
        self.ensure_one()
        self.write({'core_id': False})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_create_contract(self):
        self.ensure_one()
        return {
            'name': _('Create New Contract'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.contract',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_olt_id': self.id,
            }
        }

    def _get_olt_connection(self):
        self.ensure_one()
        return OLTConnection(
            host=self.ip,
            port=(self.port_ssh if self.type_connection=='ssh'  else self.port_telnet),
            username=self.username,
            password=self.password,
            connection_type=self.type_connection,
        )

    @api.onchange('node_id')
    def changenode(self):
        self.core_id = None

   # @api.onchange('node_id')
    @api.onchange('core_id')
    def _compute_hostname(self):
        print(('h1', self))

        olt = self

        if not olt.core_id:
            olt.name = ''
            return

        olts = self.env['silver.olt'].search([('core_id', '=', olt.core_id.id)])
        i = 1
        for o in olts:
            if o.name:
                patron = r'(\d+)$'
                match = re.search(patron, o.name)
                print(("re", match, i, o))
                if not match: continue
                if (olt._origin.id == o.id): continue
                on = int(match.group(1))
                print(("on", on, o.id, olt.id, o.id==olt.id, olt._origin.id==o.id))
                if on >= i: i = on+1


        name = f"{olt.core_id.name}/OLT{i}"

        # Construimos el código.
        # Si el campo 'code' del nodo es 'u', y ya tiene 2 OLTs, el nuevo será 'u/2'
        olt.name = name
        print(("h3", olt.name))

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

        reload_action = {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

        ostate = self.state
        ohostname = self.hostname_olt

        try:
            with self._get_olt_connection() as conn:
                # GEMINI: La conexión real y el login ocurren dentro del __enter__ de OLTConnection.
                # Si el 'with' se ejecuta sin errores, la conexión fue exitosa.
                # Ahora podemos obtener el hostname capturado.

               # with self.env.registry.cursor() as cr:
                   # if conn.hostname_olt:
                      #  self.write({'hostname_olt': conn.hostname_olt})
                   #     _logger.info(f"Hostname de la OLT '{self.name}' actualizado a '{conn.hostname_olt}'.")
                  #  else:
                   #     _logger.warning(
                   #         f"No se pudo determinar el hostname para la OLT '{self.name}' durante la conexión.")

                    # GEMINI: Actualizar el estado a 'connected' en caso de éxito.
                    #self.netdev_id.write({'state': 'active'})
                    #cr.commit()
                self.state = 'active'
                self.hostname_olt = conn.hostname_olt
                if (ostate != 'active') or (ohostname != conn.hostname_olt):
                    return True

            return [{
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Éxito',
                    'sticky': False,
                    'message': 'Conexión a la OLT exitosa!',
                    'type': 'success',
                }
            },  reload_action]
        except (ConnectionError, UserError) as e:
            print(("noe",e, ostate))
            # GEMINI: Actualizar el estado a 'error' en caso de fallo.
            #with self.env.registry.cursor() as cr:
            #    self.netdev_id.write({'state': 'down'})
            #    cr.commit()
            if (ostate != 'down'):
                self.state = 'down'
                return True
            print(("noo"))
            return [{
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'sticky': False,
                    'message': f'Conexión a la OLT fallida! {e}',
                    'type': 'danger',
                }
                   }, reload_action]
        except Exception as e:
            if (ostate != 'down'):
                self.state = 'down'
                return True
            # GEMINI: Actualizar el estado a 'error' en caso de fallo.
            #if self.netdev_id:
            #    self.netdev_id.write({'state': 'error'})
           # raise UserError(f"Un error inesperado ocurrió: {e}")
            return [{
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'sticky': False,
                    'message': f'Error en la OLT fallida! {e}',
                    'type': 'danger', }
                   }, reload_action]

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
            for ret in record.ip_address_pool_ids:
                print(("ret", ret))
                ret.action_generate_ips()


    def action_disable_onu(self, pon_port, onu_id):
        """
        Deshabilita (corta) una ONU en una OLT V-SOL.
        :param pon_port: El puerto PON (ej. '0/1').
        :param onu_id: El ID numérico de la ONU a deshabilitar (ej. 1).
        """
        self.ensure_one()
        if not all([pon_port, onu_id]):
            raise UserError("Se requieren el Puerto PON y el ID de la ONU.")

        commands = [
            "enable",
            "configure terminal",
            f"interface gpon {pon_port}",
            f"ont port {onu_id} 1 disable",
            "exit",
            "exit",
            "write",
        ]



        output_log = ""
        try:
            with self._get_olt_connection() as conn:
                for command in commands:
                    success, response, output = conn.execute_command(command)
                    output_log += f"$ {command}\n{output}\n"
                    if not success:
                        raise UserError(f"Error ejecutando el comando '{command}':\n{output}")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Éxito',
                    'message': f'ONU {onu_id} en puerto {pon_port} deshabilitada exitosamente.',
                    'type': 'success',
                }
            }
        except (ConnectionError, UserError) as e:
            raise UserError(f"Fallo al deshabilitar la ONU:\n{e}\n\nLog:\n{output_log}")
        except Exception as e:
            raise UserError(f"Un error inesperado ocurrió: {e}\n\nLog:\n{output_log}")

    def action_enable_onu(self, pon_port, onu_id):
        """
        Habilita (reconecta) una ONU en una OLT V-SOL.
        :param pon_port: El puerto PON (ej. '0/1').
        :param onu_id: El ID numérico de la ONU a habilitar (ej. 1).
        """
        self.ensure_one()
        if not all([pon_port, onu_id]):
            raise UserError("Se requieren el Puerto PON y el ID de la ONU.")

        commands = [
            "enable",
            "configure terminal",
            f"interface gpon {pon_port}",
            f"ont port {onu_id} 1 enable",
            "exit",
            "exit",
            "write",
        ]


        output_log = ""
        try:
            with self._get_olt_connection() as conn:
                for command in commands:
                    success, response, output = conn.execute_command(command)
                    output_log += f"$ {command}\n{output}\n"
                    if not success:
                        raise UserError(f"Error ejecutando el comando '{command}':\n{output}")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Éxito',
                    'message': f'ONU {onu_id} en puerto {pon_port} habilitada exitosamente.',
                    'type': 'success',
                }
            }
        except (ConnectionError, UserError) as e:
            raise UserError(f"Fallo al habilitar la ONU:\n{e}\n\nLog:\n{output_log}")
        except Exception as e:
            raise UserError(f"Un error inesperado ocurrió: {e}\n\nLog:\n{output_log}")
