# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import math
from odoo.exceptions import UserError

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
    ip_address = fields.Many2one('silver.ip.address', string="Dirección IP Asignada", domain="[('status', '=', 'available')]")
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
    olt_status = fields.Selection([
        ('unknown', 'Desconocido'),
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('los', 'LOS'),
    ], string="Estado OLT", default='unknown', readonly=True, copy=False)

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
    brand_name = fields.Char(string='Marca ONU', related='stock_lot_id.product_id.product_brand_id.name', readonly=True, store=False)
    model_name = fields.Char(string='Modelo ONU', related='stock_lot_id.product_id.model', readonly=True, store=False)
    software_version = fields.Char(string='Versión de Software ONU', related='stock_lot_id.software_version', readonly=True, store=False)

    firmware_version = fields.Char(string='Firmware Version ONU', related='stock_lot_id.firmware_version', readonly=True, store=False)
    serial_number = fields.Char(string='Serial ONU', related='stock_lot_id.serial_number', readonly=True, store=False)


    # --- Campos de Estado de Aprovisionamiento ---
    wan_config_successful = fields.Boolean(string="Configuración WAN Exitosa", default=False, readonly=True, copy=False)
    wifi_config_successful = fields.Boolean(string="Configuración WiFi Exitosa", default=False, readonly=True, copy=False)

    def action_provision_base(self):
        """Acción para ejecutar el aprovisionamiento base y activar el contrato."""
        self.ensure_one()
        if self.link_type == 'fiber' and self.olt_id:
            self.olt_id.provision_onu_base(self)
            self.write({
                'state_service': 'active',
                'date_active': fields.Date.context_today(self)
            })
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

        # Campos que podemos actualizar en caliente en la OLT
        updatable_fields = ['pppoe_user', 'pppoe_password', 'sssid', 'password']
        
        # Si alguno de los campos modificados está en nuestra lista, procedemos
        if any(field in vals for field in updatable_fields):
            for contract in self.filtered(lambda c: c.state_service == 'active' and c.link_type == 'fiber' and c.olt_id):
                commands = []
                
                # --- Construcción de Comandos Específicos ---
                # El contrato ya tiene los nuevos valores gracias al super() de arriba
                
                # Actualizar WAN PPPoE si cambiaron las credenciales
                if 'pppoe_user' in vals or 'pppoe_password' in vals:
                    if contract.pppoe_user and contract.pppoe_password and not contract.is_bridge:
                        commands.append(f"onu {contract.onu_pon_id} wan ip-mode pppoe vlan {contract.vlan_id} username {contract.pppoe_user} password {contract.pppoe_password}")

                # Actualizar WiFi si cambió el SSID o la contraseña
                if 'sssid' in vals and contract.sssid and not contract.is_bridge:
                    commands.append(f"onu {contract.onu_pon_id} wifi ssid {contract.sssid}")

 # onu 32 pri wifi_ssid 5 name SILVERDATA hide disable auth_mode wpapsk/wpa2psk encrypt_type tkipaes shared_key 25867855##13592075 rekey_interval 0

                if 'password' in vals and contract.password and not contract.is_bridge:
                    commands.append(f"onu {contract.onu_pon_id} wifi key {contract.password}")

                if commands:
                    # Si hay comandos que ejecutar, los envolvemos en la secuencia de configuración
                    full_sequence = [
                        "configure terminal",
                        f"interface gpon {contract.olt_port_id.name}",
                    ] + commands + [
                        "exit",
                        "exit",
                        "write",
                    ]

                    # --- Ejecución de Comandos ---
                    netdev = contract.olt_id.netdev_id
                    if not netdev:
                        raise UserError(f"La OLT {contract.olt_id.name} no tiene un dispositivo de red configurado.")
                    
                    try:
                        with netdev._get_olt_connection() as conn:
                            for command in full_sequence:
                                success, output = conn.execute_command(command)
                                if not success:
                                    # Si un comando falla, lo notificamos pero no detenemos el guardado
                                    # El cambio ya está en Odoo, pero falló en la OLT
                                    self.env.user.notify_warning(
                                        message=f"El cambio se guardó en Odoo, pero falló la actualización en la OLT para el contrato {contract.name}.\nComando: {command}\nError: {output}"
                                    )
                                    break 
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
            wizard = self.env['silver.provisioning.wizard'].create({'contract_id': self.id})
            return {
                'name': _('Cortar Servicio OLT'),
                'type': 'ir.actions.act_window',
                'res_model': 'silver.provisioning.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
                'context': {'action': 'cutoff', 'hide_serial': True}
            }
        super(IspContract, self).action_cutoff_service()

    def action_reconnection_service_button(self):
        self.ensure_one()
        if self.link_type == 'fiber' and self.olt_id:
            wizard = self.env['silver.provisioning.wizard'].create({'contract_id': self.id})
            return {
                'name': _('Reconectar Servicio OLT'),
                'type': 'ir.actions.act_window',
                'res_model': 'silver.provisioning.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new',
                'context': {'action': 'reconnection', 'hide_serial': True}
            }
        super(IspContract, self).action_reconnection_service_button()

    def action_suspend_service(self):
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
                    existing = secrets_path.get(name=contract.pppoe_user)
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
        return True

    def action_terminate_service(self):
        for contract in self:
            if contract.state == 'closed':
                raise UserError(_("Este contrato ya ha sido dado de baja."))

            # --- Lógica de Terminación para PPPoE en Mikrotik ---
            if contract.pppoe_user and contract.core_id:
                api = contract.core_id._get_api_connection()
                if not api:
                    raise UserError(_("No se pudo conectar al Core Router Mikrotik."))
                try:
                    secrets_path = api.path('/ppp/secret')
                    existing = secrets_path.get(name=contract.pppoe_user)
                    if existing:
                        secrets_path.remove(id=existing[0]['.id'])
                except Exception as e:
                    raise UserError(_("Fallo al eliminar el usuario PPPoE en el Core: %s") % e)
                finally:
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
        # LÓGICA OLT: Esta acción es para OLTs.
        # 1. Conectar a la OLT (self.olt_id).
        # 2. Ejecutar el comando para reiniciar la ONU.
        #    Ejemplo conceptual: ont reboot <puerto> <serial>
        raise UserError("Función no implementada. Requiere integración con la API de la OLT.")

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

    def action_check_olt_status(self):
        self.ensure_one()
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
        raise UserError("Función no implementada. Requiere integración con la API de la OLT para actualizar el estado.")
        # Ejemplo de cómo se vería al final:
        # status = self.olt_id.get_onu_status(self.olt_port_id, self.serial_onu)
        # self.write({'olt_status': status})
        return True
