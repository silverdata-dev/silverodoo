# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import math
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia entre dos puntos geográficos
    utilizando la fórmula de Haversine.
    """
    R = 6371  # Radio de la Tierra en kilómetros
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


class IspContract(models.Model):
    _inherit = 'silver.contract'


    _inherits = {
                 'silver.netdev':'netdev_id'}

    netdev_id = fields.Many2one('silver.netdev', required=True, ondelete="cascade")


    access_point_id = fields.Many2one('silver.access_point', string='Punto de Acceso')
    mac_address = fields.Char(string='Dirección MAC')
    vlan_id = fields.Many2one('silver.vlan', string='VLAN')
    olt_card_id = fields.Many2one('silver.olt.card', string='Tarjeta OLT')
    radius_id = fields.Many2one('silver.radius', string='Servidor Radius')
    notes = fields.Text(string='Notas')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    # --- Pestaña: Servicio Internet ---
    link_type = fields.Selection([
        ('fiber', 'Fibra Óptica'), ('wifi', 'Inalámbrico'),
        ('lan', 'LAN'), ('fttb', 'FTTB'),
    ], string="Tipo de Conexión", default='fiber', required=True)
    node_id = fields.Many2one('silver.node', string="Nodo")
    core_id = fields.Many2one('silver.core', string="Core Router")
    ap_id = fields.Many2one('silver.ap', string="Access Point")
    splitter_id = fields.Many2one('silver.splitter', string="Splitter")
    olt_id = fields.Many2one('silver.olt', string="OLT")
    olt_port_id = fields.Many2one('silver.olt.card.port', string="Puerto OLT")
    onu_pon_id = fields.Integer(string="ID de ONU en PON")
    box_id = fields.Many2one('silver.box', string="Caja NAP")
    #port_nap = fields.Char(string="Puerto en CTO")
    onu_id = fields.Many2one('silver.netdev', string="ONU/CPE")
#    serial_onu = fields.Char(string="Serial ONU", related="serial_number")
#    model_onu = fields.Char(string="Modelo ONU", related="serial_number"))
    is_bridge = fields.Boolean(string="ONU en modo Bridge")
    ip_address = fields.Many2one('silver.ip.address', string="Dirección IP Asignada", domain="[('status', '=', 'available')]" )
    pppoe_user = fields.Char(string="Usuario PPPoE")
    pppoe_password = fields.Char(string="Contraseña PPPoE")
    mac_address_onu = fields.Char(string="MAC Address ONU")
    date_active = fields.Date(string="Fecha de Activación", readonly=True)
    date_reconnection = fields.Date(string="Fecha de Reconexión", readonly=True)
    date_cut = fields.Date(string="Fecha de Corte", readonly=True)
    date_renovation = fields.Date(string="Fecha de Renovación", readonly=True)
    sssid = fields.Char(string="SSID (Nombre WiFi)")
    password = fields.Char(string="Contraseña WiFi")
    wifi_line_ids = fields.One2many('silver.contract.wifi.line', 'contract_id', string="Redes WiFi")
    custom_channel_id = fields.Many2one('silver.wifi.channel.line', string="Canal WiFi")
    contract_mode_wan_ids = fields.One2many('silver.contract.wan.mode', 'contract_id', string="Configuración WAN")
    new_ip_address_id = fields.Many2one('silver.ip.pool.line', string="IP de Pool")
    consumption_ids = fields.One2many('silver.contract.consumption', 'contract_id', string="Registros de Consumo")
    radius_entry_ids = fields.One2many('silver.contract.radius.entry', 'contract_id', string="Entradas de RADIUS")
    olt_state = fields.Selection([('down', 'Down'), ('active', 'Active'), ('connected', 'Connected'),
                              ('connecting', 'Connecting'),
                              ('disconnected', 'Disconnected'),
                              ('error', 'Error')],
                             related='olt_id.netdev_id.state',
                             string='Estado OLT', default='down')


    discovered_onu_id = fields.Many2one(
        'silver.olt.discovered.onu',
        string='ONU Descubierta',
        help="Seleccione una ONU de la lista de equipos descubiertos por la OLT."
    )

    temp_onu_serial_display = fields.Char(string="Serial ONU Seleccionado", readonly=True)

    @api.onchange('discovered_onu_id')
    def _onchange_discovered_onu_id(self):
        """
        Al seleccionar una ONU descubierta, llama al método centralizado para obtener
        los valores y actualiza el formulario.
        """
        if self.discovered_onu_id:
            vals = self._prepare_contract_values_from_onu(self.discovered_onu_id)
            self.update(vals)
        else:
            # Opcional: limpiar los campos si se deselecciona la ONU
            self.update({
                'temp_onu_serial_display': False,
                'serial_number': False,
                'model_name': False,
                'stock_lot_id': False,
                'olt_card_id': False,
                'olt_port_id': False,
                'onu_pon_id': False,
            })

    def _prepare_contract_values_from_onu(self, discovered_onu):
        """
        Método centralizado que procesa una ONU descubierta y devuelve un
        diccionario de valores para ser escritos en el contrato.
        """
        self.ensure_one()
        if not discovered_onu:
            return {}

        StockLot = self.env['stock.lot']
        OltCard = self.env['silver.olt.card']
        OltPort = self.env['silver.olt.card.port']

        serial_number = discovered_onu.serial_number
        olt_index = discovered_onu.olt_index

        # --- Buscar o crear Lote/Serial ---
        lot = StockLot.search([('name', '=', serial_number)], limit=1)
        if not lot:
            lot = StockLot.create({
                'name': serial_number,
                'model_name': discovered_onu.model_name,
                'product_id': None,
                'external_equipment': True,
                'software_version': discovered_onu.version,
                'company_id': self.company_id.id or self.env.company.id,
            })

        # --- Parsear olt_index y buscar/crear Tarjeta y Puerto ---
        card = None
        port = None
        onu_pon_id = None
        if olt_index and 'GPON' in olt_index and self.olt_id:
            try:
                clean_index = olt_index.replace('GPON', '')
                card_str, port_pon_str = clean_index.split('/')
                port_str, pon_id_str = port_pon_str.split(':')

                card_index = int(card_str)
                port_index = int(port_str)
                onu_pon_id = int(pon_id_str)

                card = OltCard.search([('olt_id', '=', self.olt_id.id), ('num_card', '=', card_index)], limit=1)
                if not card:
                    card = OltCard.create({
                        'olt_id': self.olt_id.id, 'num_card': card_index,
                        'name': f"{self.olt_id.name}/C{card_index}",
                    })

                if card:
                    port = OltPort.search([('olt_card_id', '=', card.id), ('num_port', '=', port_index)], limit=1)
                    if not port:
                        port = OltPort.create({
                            'olt_card_id': card.id, 'num_port': port_index,
                            'name': f"{card.name}/P{port_index}",
                        })
            except (ValueError, IndexError):
                pass

        # --- Devolver el diccionario de valores ---
        return {
            'temp_onu_serial_display': serial_number,
            'serial_number': serial_number,
            'model_name': discovered_onu.model_name,
            'stock_lot_id': lot.id,
            'olt_card_id': card.id if card else False,
            'olt_port_id': port.id if port else False,
            'onu_pon_id': onu_pon_id,
        }

    def action_open_onu_selector_wizard(self):
        """
        Botón en el contrato para refrescar la lista de ONUs y abrir el asistente de selección.
        """
        self.ensure_one()
        if not self.olt_id:
            raise UserError(_("Por favor, seleccione una OLT primero."))
        
        # Primero, ejecuta el descubrimiento en segundo plano para asegurar que la lista está actualizada.
        self.olt_id.action_discover_onus()

        # Luego, devuelve la acción para abrir el asistente.
        return {
            'name': _('Seleccionar ONU Descubierta'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.contract.select.onu.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_contract_id': self.id,
            }
        }

    @api.model
    def create(self, vals):
        """
        Sobrescritura para generar las redes WiFi por defecto en la creación del contrato.
        """
        # Comprobar si se está creando un contrato con un cliente y sin líneas WiFi predefinidas
        if vals.get('partner_id') and not vals.get('wifi_line_ids'):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            if partner.vat:
                # Generar las líneas WiFi por defecto
                default_lines = [
                    (0, 0, {
                        'ssid_index': 1,
                        'name': 'SILVERDATA',
                        'password': partner.vat,
                    }),
                    (0, 0, {
                        'ssid_index': 5,
                        'name': 'SILVERDATA-5G',
                        'password': partner.vat,
                    }),
                ]
                # Añadirlas al diccionario de valores de creación
                vals['wifi_line_ids'] = default_lines
        
        return super(IspContract, self).create(vals)

    #  serial_onu = fields.Many2one('stock.production.lot', string="Serial ONU")
    pppoe = fields.Char(string="PPPoe")
    password_pppoe = fields.Char(string="Contrasena PPPoe")
    wan_mode = fields.Selection([], string="WAN mode")
    is_router_wifi = fields.Boolean(string="Router")
    password_wam = fields.Char(string="Password")
    ip_public = fields.Char(string="Ip Public")
    is_ip_public = fields.Boolean(string="IP Pública")

    stock_lot_id = fields.Many2one(
        'stock.lot',
        string='Equipo (Serie/Lote)',
        related='netdev_id.stock_lot_id',
        readonly=False,
        store=False,
    )
    brand_name = fields.Char(string='Marca ONU', related='stock_lot_id.brand_name', readonly=True, store=False)
    model_name = fields.Char(string='Modelo ONU', related='stock_lot_id.model_name', readonly=True, store=False)
    software_version = fields.Char(string='Versión de Software ONU', related='stock_lot_id.software_version', readonly=True, store=False)

    firmware_version = fields.Char(string='Firmware Version ONU', related='stock_lot_id.firmware_version', readonly=True, store=False)
    serial_number = fields.Char(string='Serial ONU', related='stock_lot_id.serial_number', readonly=True, store=False)

    # GEMINI: Nuevo campo para el estado de conexión PPPoE
    pppoe_state = fields.Selection([('down', 'Down'), ('active', 'Active'), ('connected', 'Connected'),
                      ('connecting', 'Connecting'),
                      ('disconnected', 'Disconnected'),
                      ('error', 'Error')],
                     string='Estado conexión PPPoE', default='down')

    # --- Campos de Estado de Aprovisionamiento ---
    wan_config_successful = fields.Boolean(string="Configuración WAN Exitosa", default=False, readonly=True, copy=False)
    wifi_config_successful = fields.Boolean(string="Configuración WiFi Exitosa", default=False, readonly=True, copy=False)

    def action_add_radius_access(self):
        """
        Crea o actualiza el usuario en el User Manager de MikroTik.
        """
        self.ensure_one()
        if not all([self.pppoe_user, self.pppoe_password, self.core_id, self.partner_id, self.plan_type_id]):
            raise UserError(_("Se requiere Usuario PPPoE, Contraseña, Core Router, Cliente y Plan para continuar."))

        api = None
        try:
            api = self.core_id.netdev_id._get_api_connection()
            if not api:
                self.pppoe_state = 'down'
                # (El resto de tu lógica de notificación de error se mantiene aquí)
                return { 'type': 'ir.actions.client', 'tag': 'display_notification', 'params': { 'title': 'Error', 'message': _("No se pudo conectar al Core Router Mikrotik."), 'type': 'danger', } }

            user_path = api.path('/user-manager/user')

            # Preparar datos del usuario para User Manager
            user_data = {
                'username': self.pppoe_user,
                'password': self.pppoe_password,
                'customer': self.partner_id.name,
                'profile': self.plan_type_id.name,
            }
            if self.mac_address:
                user_data['caller-id'] = self.mac_address

            print(("user", user_data, tuple(user_path)))

            existing = tuple(user_path('print', { 'username': self.pppoe_user}))

            if existing:
                # Actualizar existente
                user_path.set(id=existing[0]['.id'], **user_data)
                message = _("Usuario '%s' actualizado exitosamente en User Manager.") % self.pppoe_user
            else:
                # Crear nuevo
                user_path.add(**user_data)
                message = _("Usuario '%s' creado exitosamente en User Manager.") % self.pppoe_user

            _logger.info(message)
            self.pppoe_state = 'active'
            # (El resto de tu lógica de notificación de éxito se mantiene aquí)
            return { 'type': 'ir.actions.client', 'tag': 'display_notification', 'params': { 'title': 'Activo', 'message': message, 'type': 'success', } }

        except Exception as e:
            error_message = _("Fallo al gestionar el usuario en User Manager: %s") % e
            _logger.error(error_message)
            self.pppoe_state = 'down'
            # (El resto de tu lógica de notificación de error se mantiene aquí)
            return { 'type': 'ir.actions.client', 'tag': 'display_notification', 'params': { 'title': 'Error', 'message': error_message, 'type': 'danger', } }
        finally:
            if api:
                api.close()

    def action_check_radius_connection(self):
        """
        Verifica el estado de la conexión PPPoE del usuario en el MikroTik.
        """
        self.ensure_one()
        if not self.pppoe_user or not self.core_id:
            raise UserError(_("Se requiere Usuario PPPoE y Core Router configurados para verificar la conexión."))


        api = None
        status_message = ""
        try:
            api = self.core_id.netdev_id._get_api_connection()
            if not api:
                self.pppoe_state = 'down'
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Error',
                        'message': _("No se pudo conectar al Core Router Mikrotik."),
                        'type': 'danger',
                    }
                }
                #raise UserError(_("No se pudo conectar al Core Router Mikrotik."))

            # GEMINI: Sintaxis moderna, tratando el recurso como callable y convirtiendo a tupla
            active_sessions = tuple(api.path('/ppp/active')('print', **{'?name': self.pppoe_user}))

            if active_sessions:
                session_info = active_sessions[0]
                status_message = _("Usuario PPPoE '%s' está ACTIVO.\nIP: %s\nUptime: %s") % (
                    self.pppoe_user, session_info.get('address', 'N/A'), session_info.get('uptime', 'N/A')
                )
                self.pppoe_connection_status = "Activo"
                self.env.user.notify_success(message=status_message)
            else:
                status_message = _("Usuario PPPoE '%s' está INACTIVO (sin sesión activa).") % self.pppoe_user
                #self.pppoe_connection_status = "Inactivo"
                #self.env.user.notify_info(message=status_message)
                self.pppoe_state = 'connected'
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Conectado',
                        'message': status_message,
                        'type': 'success',
                    }
                }

        except Exception as e:
            status_message = _("Fallo al verificar la conexión PPPoE en MikroTik: %s") % e

            self.pppoe_state = 'down'
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': status_message,
                    'type': 'danger',
                }
            }
            #self.pppoe_connection_status = f"Error: {e}"
            #self.env.user.notify_warning(message=status_message)
            #raise UserError(status_message)
        finally:
            if api:
                api.close()

    def action_provision_base(self):
        """
        Acción para ejecutar el aprovisionamiento base, activar el contrato,
        y luego intentar las configuraciones de WAN y WiFi sin fallar.
        """
        self.ensure_one()
        if self.link_type == 'fiber' and self.olt_id:
            # 1. Ejecutar el aprovisionamiento base. Este paso es crítico.
            self.olt_id.provision_onu_base(self)
            
            # 2. Si la base fue exitosa, activar el servicio en Odoo.
            self.write({
                'state_service': 'active',
                'date_active': fields.Date.context_today(self)
            })

            # 3. Intentar la configuración WAN. Si falla, solo notificar.
        #    try:
        #        if self.olt_id.is_gestion_pppoe:
        #            self.olt_id.provision_onu_wan(self)
        #            self.write({'wan_config_successful': True})
        #    except Exception as e:
                #print(("fallo", e))
                #self.env.user.notify_warning(
                #    message=f"Aprovisionamiento base exitoso, pero falló la configuración WAN.\nError: {e}"
                #)
        #        pass

            # 4. Intentar la configuración WiFi. Si falla, solo notificar.
        #    try:
        #        self.olt_id.provision_onu_wifi(self)
        #        self.write({'wifi_config_successful': True})
        #    except Exception as e:
        #        pass
                #self.env.user.notify_warning(
                #    message=f"Aprovisionamiento base exitoso, pero falló la configuración WiFi.\nError: {e}"
                #)
                
        return True

    def action_provision_wan(self):
        """Acción para ejecutar la configuración WAN avanzada."""
        self.ensure_one()
        if self.link_type == 'fiber' and self.olt_id:
            self.olt_id.provision_onu_wan(self)
            self.write({'wan_config_successful': True})
        return True

    def action_provision_wifi(self):
        """Acción para ejecutar la configuración WiFi."""
        self.ensure_one()
        if self.link_type == 'fiber' and self.olt_id:
            self.olt_id.provision_onu_wifi(self)
            self.write({'wifi_config_successful': True})
        return True

    def write(self, vals):
        # Si se modifican las líneas de WiFi, reseteamos el flag de éxito.
        if 'wifi_line_ids' in vals:
            vals['wifi_config_successful'] = False
            
        # Primero, ejecutar el write original para guardar los cambios en la BD
        res = super(IspContract, self).write(vals)

        # --- Lógica de Aprovisionamiento en Caliente para OLT ---
        # Campos cuya modificación dispara una actualización en la OLT
        updatable_fields = [
            'pppoe_user', 'pppoe_password', 'wifi_line_ids', 'is_bridge', 
            'product_id', 'vlan_id'
        ]
        
        # Proceder solo si se ha modificado al menos un campo relevante
        if any(field in vals for field in updatable_fields):
            for contract in self.filtered(lambda c: c.state_service == 'active' and c.link_type == 'fiber' and c.olt_id and c.olt_port_id and c.onu_pon_id):
                
                olt = contract.olt_id
                commands = []

                # --- 1. Gestión de Cambios en la Configuración WAN (Bridge/Router/PPPoE/VLAN) ---
                wan_fields = ['is_bridge', 'vlan_id', 'pppoe_user', 'pppoe_password']
                if any(field in vals for field in wan_fields) and olt.is_gestion_pppoe:
                    if contract.is_bridge and olt.is_activation_bridge:
                        # Modo Bridge: solo requiere VLAN
                        commands.append(f"ont ipconfig {contract.olt_port_id.name} {contract.onu_pon_id} ip-index 1 dhcp-enable enable vlan-id {contract.vlan_id.name}")
                        commands.append(f"ont wan {contract.olt_port_id.name} {contract.onu_pon_id} ip-index 1 mode bridge")

                    elif not contract.is_bridge:
                        # Modo Router (asumimos PPPoE si hay credenciales)
                        if contract.pppoe_user and contract.pppoe_password:
                            commands.append(f"ont ipconfig {contract.olt_port_id.name} {contract.onu_pon_id} ip-index 1 pppoe-enable enable username {contract.pppoe_user} password {contract.pppoe_password} vlan-id {contract.vlan_id.name}")
                            commands.append(f"ont wan {contract.olt_port_id.name} {contract.onu_pon_id} ip-index 1 mode pppoe")

                # --- 2. Gestión de Cambio de Plan (Ancho de Banda) ---
                if 'product_id' in vals and olt.is_control_traffic_profile:
                    new_product = self.env['product.product'].browse(vals['product_id'])
                    # Asumimos que el product.template tiene una referencia al perfil de tráfico
                    if new_product and hasattr(new_product, 'traffic_profile_id') and new_product.traffic_profile_id:
                        profile_name = new_product.traffic_profile_id.name
                        commands.append(f"ont traffic-profile {contract.olt_port_id.name} {contract.onu_pon_id} profile-name {profile_name}")

                # --- 3. Gestión de Cambios en WiFi ---
                if 'wifi_line_ids' in vals:
                    for command_tuple in vals['wifi_line_ids']:
                        # command_tuple es de la forma (0, 0, {vals}), (1, id, {vals}), (2, id, _)
                        op, line_id, line_vals = command_tuple[0], command_tuple[1], command_tuple[2] if len(command_tuple) > 2 else {}
                        
                        if op == 1 and line_vals: # Actualización de una línea existente
                            line = self.env['silver.contract.wifi.line'].browse(line_id)
                            ssid_index = line.ssid_index
                            
                            if 'name' in line_vals:
                                commands.append(f"ont wifi {contract.olt_port_id.name} {contract.onu_pon_id} ssid-index {ssid_index} ssid {line_vals['name']}")
                            if 'password' in line_vals:
                                commands.append(f"ont wifi {contract.olt_port_id.name} {contract.onu_pon_id} ssid-index {ssid_index} password {line_vals['password']}")

                # --- Ejecución de Comandos si se generó alguno ---
                if commands:
                    full_sequence = [
                        "enable",
                        "configure terminal",
                    ] + commands + [
                        "exit",
                    ]
                    if olt.is_write_olt:
                        full_sequence.append("write")

                    netdev = olt.netdev_id
                    if not netdev:
                        self.env.user.notify_warning(
                            message=f"La OLT {olt.name} no tiene un dispositivo de red configurado."
                        )
                        continue

                    try:
                        with netdev._get_olt_connection() as conn:
                            for command in full_sequence:
                                success, response, output = conn.execute_command(command)
                                if not success:
                                    self.env.user.notify_warning(
                                        message=f"Un comando falló en la OLT para el contrato {contract.name}.\nComando: {command}\nError: {output}"
                                    )
                                    break  # Detener si un comando falla
                    except Exception as e:
                        self.env.user.notify_warning(
                            message=f"No se pudo conectar a la OLT para actualizar el contrato {contract.name}.\nError: {e}"
                        )
        return res

    def action_activate_service(self):
        self.ensure_one()
        if self.link_type == 'fiber' and self.olt_id:
            # Llamada directa al método de aprovisionamiento de la OLT
            self.olt_id.action_provision_onu(self)
            
            # Si el método anterior no lanza una excepción, la provisión fue exitosa.
            self.write({
                'state_service': 'active',
                'date_active': fields.Date.context_today(self)
            })
            
            # Devolver una notificación de éxito al usuario
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Éxito'),
                    'message': _('El servicio ha sido aprovisionado y activado correctamente.'),
                    'type': 'success',
                }
            }
        # Fallback to original PPPoE logic if not fiber
        super(IspContract, self).action_activate_service()

    def action_cutoff_service(self):
        self.ensure_one()
        if self.link_type == 'fiber' and self.olt_id:
            self.olt_id.disable_onu(self)
            self.write({
                'state_service': 'disabled',
                'date_cut': fields.Date.context_today(self)
            })
            return True
        return super(IspContract, self).action_cutoff_service()

    def action_reconnection_service_button(self):
        self.ensure_one()
        if self.link_type == 'fiber' and self.olt_id:
            self.olt_id.enable_onu(self)
        self.write({
            'state_service': 'active',
            'date_reconnection': fields.Date.context_today(self)
        })
        return True

    def action_suspend_service(self):
        self.ensure_one()
        if self.link_type == 'fiber' and self.olt_id:
            self.olt_id.disable_onu(self)
        self.write({
            'state_service': 'suspended',
            'date_reconnection': fields.Date.context_today(self)
        })
        return True
        """
        for contract in self:
            if contract.state_service != 'active':
                raise UserError(_("El servicio no está activo, por lo tanto no se puede suspender."))

            # --- Lógica de Suspensión para PPPoE en Mikrotik ---
            if contract.pppoe_user and contract.core_id:
                api = contract.core_id._get_api_connection()
                if not api:
                    raise UserError(_("No se pudo conectar al Core Router Mikrotik."))
                try:
                    secrets_path = api.path('/ppp/secret')
                    existing = tuple(secrets_path(name=contract.pppoe_user))
                    if existing:
                        # La suspensión se maneja cambiando el perfil a uno de "Suspendido"
                        # Este perfil debe existir en el Mikrotik con velocidad limitada o redirección.
                        secrets_path.set(id=existing[0]['.id'], profile='suspendido')
                except Exception as e:
                    raise UserError(_("Fallo al suspender el usuario PPPoE en el Core: %s") % e)
                finally:
                    api.close()

            # --- Lógica de Suspensión para OLT (Fibra Óptica) ---
            elif contract.link_type == 'fiber':
                # LÓGICA OLT: Algunas OLTs permiten cambiar el perfil de servicio de la ONU a uno de "corte" o "suspensión".
                # Ejemplo conceptual: service-port <vlan> ... inbound <perfil_suspendido> outbound <perfil_suspendido>
                pass

            contract.write({'state_service': 'suspended'})
        return True"""

    def action_terminate_service(self):
        for contract in self:
            if contract.state == 'closed':
                raise UserError(_("Este contrato ya ha sido dado de baja."))

            # --- Lógica de Terminación para PPPoE en Mikrotik (User Manager) ---
            if contract.pppoe_user and contract.core_id:
                api = None
                try:
                    api = contract.core_id.netdev_id._get_api_connection()
                    if not api:
                        raise UserError(_("No se pudo conectar al Core Router Mikrotik."))
                    
                    user_path = api.path('/user-manager/user')
                    existing = tuple(user_path('print', **{'?name': contract.pppoe_user}))
                    
                    if existing:
                        user_path.remove(id=existing[0]['.id'])
                
                except Exception as e:
                    self.env.user.notify_warning(
                        message=_("Fallo al eliminar el usuario de User Manager para el contrato %s: %s") % (contract.name, e)
                    )
                finally:
                    if api:
                        api.close()

            # --- Lógica de Terminación para OLT (Fibra Óptica) ---
            elif contract.link_type == 'fiber':
                # LÓGICA OLT: Eliminar completamente la configuración de la ONU.
                # Ejemplo conceptual: ont delete <puerto_olt> <serial_onu>
                pass

            contract.write({
                'state': 'closed',
                'date_end': fields.Date.context_today(self)
            })
        return True

    def action_ping_service(self):
        self.ensure_one()
        if not self.ip_address or not self.ip_address.name:
            raise UserError(_("No hay ninguna dirección IP asignada a este contrato para hacer ping."))
        if not self.core_id:
            raise UserError(_("No se ha configurado un router principal (Core) para ejecutar el ping."))

        ping_result_str = ""
        try:
            api = self.core_id._get_api_connection()
            if not api:
                raise UserError(_("No se pudo conectar al Core Router Mikrotik."))
            
            try:
                # El comando ping en la API de Mikrotik devuelve un iterador.
                ping_results = api(cmd='/ping', address=self.ip_address.name, count='5')
                for result in ping_results:
                    ping_result_str += f"{result}\n"
            except Exception as e:
                 ping_result_str = _("Fallo la ejecución del ping: %s") % e
            finally:
                api.close()

        except Exception as e:
            ping_result_str = _("Error de conexión: %s") % e

        wizard = self.env['silver.ping.wizard'].create({'ping_output': ping_result_str})
        return {
            'name': _('Resultado de Ping'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.ping.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def action_status_olt(self):
        # LÓGICA OLT: Esta acción es puramente para OLTs.
        # 1. Conectar a la OLT (self.olt_id) vía Telnet, SSH, etc.
        # 2. Ejecutar el comando para ver el estado óptico de la ONU.
        #    Ejemplo conceptual: display ont optical-info <puerto> <serial>
        # 3. Parsear la respuesta para obtener valores como la potencia de recepción (Rx Power).
        # 4. Mostrar esta información en un asistente (wizard) en Odoo.
        raise UserError("Función no implementada. Requiere integración con la API de la OLT.")

    def action_test_speed_service(self):
        # LÓGICA TEST DE VELOCIDAD:
        # Esta es una función compleja. La API de Mikrotik ('/tool/bandwidth-test') requiere un cliente
        # de BTest en el otro extremo, lo cual no es estándar en los equipos de cliente.
        # Alternativas:
        # 1. Instalar un servidor Speedtest (Ookla) en tu red y tener un agente en el CPE del cliente.
        # 2. Usar protocolos como TR-069 para instruir al CPE que realice un test de velocidad.
        # 3. Integrarse con una plataforma externa de monitoreo de red.
        raise UserError("Función no implementada. Requiere una infraestructura de test de velocidad dedicada.")

    def action_remove_service(self):
        # Este botón parece redundante con "Dar de Baja". Si la intención es diferente,
        # se debería clarificar el propósito. Por ahora, lo dejamos sin implementación.
        raise UserError("Función no implementada.")

    def action_contract_reboot_onu(self):
        self.ensure_one()
        if self.link_type == 'fiber' and self.olt_id:
            self.olt_id.reboot_onu(self)
            return True
        raise UserError("Función no implementada para este tipo de conexión.")

    def action_change_ont_service(self):
        # LÓGICA DE PROCESO: Esta acción es más un proceso de Odoo que una interacción directa.
        # 1. Abrir un asistente (wizard) que pida el número de serie de la nueva ONU.
        # 2. El asistente podría crear una tarea en el proyecto de soporte técnico para que un técnico
        #    realice el cambio físico.
        # 3. Una vez que el técnico confirma, se actualiza el campo 'serial_onu' en el contrato.
        # 4. Luego se podría llamar a la lógica de (re)provisión para la nueva ONU en la OLT.
        raise UserError("Función no implementada. Se recomienda implementarla como un asistente de Odoo.")

    @api.onchange('silver_address_id')
    def _onchange_silver_address_id(self):
        if self.silver_address_id and self.silver_address_id.latitude and self.silver_address_id.longitude:
            lat = self.silver_address_id.latitude
            lon = self.silver_address_id.longitude

            # Encuentra el nodo más cercano
            nodes = self.env['silver.node'].search([])
            closest_node = None
            min_dist_node = float('inf')
            for node in nodes:
                if node.asset_id.latitude and node.asset_id.longitude:
                    dist = haversine(lat, lon, node.asset_id.latitude, node.asset_id.longitude)
                    if dist < min_dist_node:
                        min_dist_node = dist
                        closest_node = node
            self.node_id = closest_node

            # Encuentra la caja NAP más cercana
            boxes = self.env['silver.box'].search([])
            closest_box = None
            min_dist_box = float('inf')
            for box in boxes:
                if box.asset_id.latitude and box.asset_id.longitude:
                    dist = haversine(lat, lon, box.asset_id.latitude, box.asset_id.longitude)
                    if dist < min_dist_box:
                        min_dist_box = dist
                        closest_box = box
            self.box_id = closest_box
        else:
            self.node_id = False
            self.box_id = False

    @api.onchange('box_id')
    def _onchange_box_id(self):
        self.core_id = False
        self.olt_id = False
        domain = {'domain': {'core_id': []}}
        if self.box_id:
            core_domain = [('node_id', '=', self.box_id.node_id.id)]
            first_core = self.env['silver.core'].search(core_domain, limit=1)
            if first_core:
                self.core_id = first_core
            domain = {'domain': {'core_id': core_domain}}
        return domain

    @api.onchange('core_id')
    def _onchange_core_id(self):
        self.olt_id = False
        domain = {'domain': {'olt_id': []}}
        if self.core_id:
            olt_domain = [('id', 'in', self.core_id.olt_ids.ids)]
            first_olt = self.env['silver.olt'].search(olt_domain, limit=1)
            if first_olt:
                self.olt_id = first_olt
            domain = {'domain': {'olt_id': olt_domain}}
        return domain

    def action_check_olt_state(self):
        self.ensure_one()
        self.olt_id.action_connect_olt()
        # LÓGICA OLT: Esta acción es puramente para OLTs.
        # 1. Conectar a la OLT (self.olt_id) vía Telnet, SSH, etc.
        # 2. Ejecutar el comando para ver el estado óptico de la ONU.
        #    Ejemplo conceptual: display ont optical-info <puerto> <serial>
        # 3. Parsear la respuesta para obtener valores como la potencia de recepción (Rx Power).
        # 4. Basado en la respuesta, actualizar el campo 'olt_status'.
        #    - Si hay respuesta y la potencia es buena: self.olt_status = 'online'
        #    - Si la ONU aparece con "Loss of Signal": self.olt_status = 'los'
        #    - Si no se puede conectar o no se encuentra la ONU: self.olt_status = 'offline'
        # 5. Por ahora, esta función solo muestra un aviso.
        #raise UserError("Función no implementada. Requiere integración con la API de la OLT para actualizar el estado.")
        # Ejemplo de cómo se vería al final:
        # status = self.olt_id.get_onu_status(self.olt_port_id, self.serial_onu)
        # self.write({'olt_status': status})
        return True