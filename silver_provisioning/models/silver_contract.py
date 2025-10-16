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
    box_id = fields.Many2one('silver.box', string="Caja NAP")
    #port_nap = fields.Char(string="Puerto en CTO")
    onu_id = fields.Many2one('silver.netdev', string="ONU/CPE")
    serial_onu = fields.Char(string="Serial ONU")
    model_onu = fields.Char(string="Modelo ONU")
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
        store=True,
    )
    brand_name = fields.Char(string='Marca', related='stock_lot_id.product_id.product_brand_id.name', readonly=True, store=True)
    model_name = fields.Char(string='Modelo', related='stock_lot_id.product_id.model', readonly=True, store=True)
    software_version = fields.Char(string='Versión de Software', related='stock_lot_id.software_version', readonly=True, store=True)

    firmware_version = fields.Char(string='Firmware Version', related='stock_lot_id.firmware_version', readonly=True, store=True)
    serial_number = fields.Char(string='Serial Number', related='stock_lot_id.serial_number', readonly=True, store=True)


    def action_activate_service(self):
        for contract in self:
            if not contract.line_ids:
                raise UserError(_("El contrato no tiene líneas de servicio (planes) definidos."))

            # --- Lógica de Provisión para PPPoE en Mikrotik ---
            if contract.pppoe_user and contract.core_id:
                api = contract.core_id._get_api_connection()
                if not api:
                    raise UserError(_("No se pudo conectar al Core Router Mikrotik."))
                try:
                    plan_name = contract.line_ids[0].product_id.name
                    secrets_path = api.path('/ppp/secret')
                    
                    # Verificar si el usuario ya existe
                    existing = secrets_path.get(name=contract.pppoe_user)
                    if existing:
                        # Si existe, lo actualizamos y habilitamos
                        secrets_path.set(
                            id=existing[0]['.id'],
                            password=contract.pppoe_password,
                            service='pppoe',
                            profile=plan_name,
                            comment=f"Contrato: {contract.name}",
                            disabled='no'
                        )
                    else:
                        # Si no existe, lo creamos
                        secrets_path.add(
                            name=contract.pppoe_user,
                            password=contract.pppoe_password,
                            service='pppoe',
                            profile=plan_name,
                            comment=f"Contrato: {contract.name}"
                        )
                except Exception as e:
                    raise UserError(_("Fallo al crear/actualizar el usuario PPPoE en el Core: %s") % e)
                finally:
                    api.close()

            # --- Lógica de Provisión para OLT (Fibra Óptica) ---
            elif contract.link_type == 'fiber':
                # LÓGICA OLT: Esta sección requiere una integración específica con la marca de tu OLT (Huawei, ZTE, FiberHome, etc.)
                # 1. Conectar a la OLT (self.olt_id) a través de su API (Telnet, SSH, SNMP, o una API REST si es moderna).
                # 2. Autenticarse con las credenciales guardadas en el modelo de la OLT.
                # 3. Ejecutar el comando para registrar y autorizar la ONU en el puerto especificado.
                #    Ejemplo conceptual para una OLT Huawei (los comandos varían mucho):
                #    ont add <puerto_olt> <serial_onu> <tipo_onu>
                #    service-port <vlan> <puerto_olt> <serial_onu> inbound <perfil_trafico> outbound <perfil_trafico>
                # Se recomienda crear un método en el modelo 'silver.olt' que encapsule esta lógica.
                # Ejemplo: contract.olt_id.provision_service_on_port(...)
                pass

            # Actualización de Estado
            contract.write({
                'state_service': 'active',
                'date_active': fields.Date.context_today(self)
            })
        return True

    def action_cutoff_service(self):
        for contract in self:
            if contract.state_service != 'active':
                raise UserError(_("El servicio no está activo, por lo tanto no se puede cortar."))

            # --- Lógica de Corte para PPPoE en Mikrotik ---
            if contract.pppoe_user and contract.core_id:
                api = contract.core_id._get_api_connection()
                if not api:
                    raise UserError(_("No se pudo conectar al Core Router Mikrotik."))
                try:
                    secrets_path = api.path('/ppp/secret')
                    existing = secrets_path.get(name=contract.pppoe_user)
                    if existing:
                        secrets_path.set(id=existing[0]['.id'], disabled='yes')
                except Exception as e:
                    raise UserError(_("Fallo al deshabilitar el usuario PPPoE en el Core: %s") % e)
                finally:
                    api.close()

            # --- Lógica de Corte para OLT (Fibra Óptica) ---
            elif contract.link_type == 'fiber':
                # LÓGICA OLT: Conectar a la OLT y ejecutar el comando para desactivar o eliminar la ONU.
                # Ejemplo conceptual: ont delete <puerto_olt> <serial_onu>
                pass

            # Actualización de Estado
            contract.write({
                'state_service': 'disabled',
                'date_cut': fields.Date.context_today(self)
            })
        return True

    def action_reconnection_service_button(self):
        for contract in self:
            if contract.state_service not in ['disabled', 'suspended']:
                raise UserError(_("El servicio no está cortado o suspendido, por lo tanto no se puede reconectar."))

            # --- Lógica de Reconexión para PPPoE en Mikrotik ---
            if contract.pppoe_user and contract.core_id:
                api = contract.core_id._get_api_connection()
                if not api:
                    raise UserError(_("No se pudo conectar al Core Router Mikrotik."))
                try:
                    secrets_path = api.path('/ppp/secret')
                    existing = secrets_path.get(name=contract.pppoe_user)
                    if existing:
                        # Al reconectar, nos aseguramos que tenga el plan correcto y esté habilitado
                        plan_name = contract.line_ids[0].product_id.name
                        secrets_path.set(id=existing[0]['.id'], disabled='no', profile=plan_name)
                except Exception as e:
                    raise UserError(_("Fallo al habilitar el usuario PPPoE en el Core: %s") % e)
                finally:
                    api.close()

            # --- Lógica de Reconexión para OLT (Fibra Óptica) ---
            elif contract.link_type == 'fiber':
                # LÓGICA OLT: Es similar a la activación. Conectar a la OLT y volver a autorizar la ONU.
                # Ejemplo conceptual: ont add ... (o un comando específico de 'ont activate')
                pass

            # Actualización de Estado
            contract.write({
                'state_service': 'active',
                'date_reconnection': fields.Date.context_today(self)
            })
        return True

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
                if node.latitude and node.longitude:
                    dist = haversine(lat, lon, node.latitude, node.longitude)
                    if dist < min_dist_node:
                        min_dist_node = dist
                        closest_node = node
            self.node_id = closest_node

            # Encuentra la caja NAP más cercana
            boxes = self.env['silver.box'].search([])
            closest_box = None
            min_dist_box = float('inf')
            for box in boxes:
                if box.latitude and box.longitude:
                    dist = haversine(lat, lon, box.latitude, box.longitude)
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
