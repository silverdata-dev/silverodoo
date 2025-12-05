# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import re
import math
from odoo.exceptions import UserError, ValidationError
import logging
from librouteros.query import Key
from datetime import datetime
from dateutil.relativedelta import relativedelta # Necesitas 'python-dateutil'

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

   # @api.constrains('ip_address_id')
    def _check_conditional_logic(self):
        for record in self:
            # Check the condition

            if record.ip_address_id : #and record.state_service == 'active':
                p = self.search([('ip_address_id', '=', record.ip_address_id.id), ('id', '!=', record.id), ('state_service', '=', 'active')])
                # Apply the constraint only if the condition is True
                print(("cond ip", p))
                if p and len(p):
                    raise ValidationError("La IP ya está ocupada")

    _sql_constraints = [
        ('ip_address_id_unique',
         'UNIQUE (ip_address_id)',
         'Esta ip está siendo utilizada.'),
            (
            "pononu_unique",
            "unique (onupon)",
            "ONU ocupada",
        )
    ]


    access_point_id = fields.Many2one('silver.access_point', string='Punto de Acceso')
    mac_address = fields.Char(string='Dirección MAC')
    vlan_id = fields.Many2one('silver.vlan', string='VLAN')#, domain="[('olt_id', '=', olt_id)]")
    olt_card_id = fields.Many2one('silver.olt.card', string='Tarjeta OLT')
    radius_id = fields.Many2one('silver.core', string='Servidor Radius')
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

    onupon = fields.Char(string='onupon', compute="_computonupon",store=True)

    ip_address_id = fields.Many2one('silver.ip.address', string="Dirección IP",)# domain="['id', 'in', ip_address_ids)]" )
    ip_address_ids = fields.One2many('silver.ip.address', 'contract_id',  string="Direcciones IPs",
                                    domain="['|', ('contract_id', '=', False), ('contract_id', '=', id)]")
    ip_address_count = fields.Integer(string="Cantidad de IPs", compute="_compute_ip_address_count", store=True)

    ppp_active = fields.Many2one('silver.netdev.ppp.active.wizard.line', string="PPP Active line")



    pppoe_user = fields.Char(string="Usuario PPPoE")
    pppoe_password = fields.Char(string="Contraseña PPPoE")

    date_active = fields.Date(string="Fecha de Activación", readonly=True)
    date_reconnection = fields.Date(string="Fecha de Reconexión", readonly=True)
    date_cut = fields.Date(string="Fecha de Corte", readonly=True)
    date_renovation = fields.Date(string="Fecha de Renovación", readonly=True)
    sssid = fields.Char(string="SSID (Nombre WiFi)")
    password = fields.Char(string="Contraseña WiFi")
    wifi_line_ids = fields.One2many('silver.contract.wifi.line', 'contract_id', string="Redes WiFi")
    custom_channel_id = fields.Many2one('silver.wifi.channel.line', string="Canal WiFi")
    contract_mode_wan_ids = fields.One2many('silver.contract.wan.mode', 'contract_id', string="Configuración WAN")

    consumption_ids = fields.One2many('silver.contract.consumption', 'contract_id', string="Registros de Consumo")
    radius_entry_ids = fields.One2many('silver.contract.radius.entry', 'contract_id', string="Entradas de RADIUS")
    olt_state = fields.Selection([('down', 'Down'), ('active', 'Activo'),
                                  ('pending', 'Prueba'),],
                             string='Estado OLT', default='pending')
    radius_state = fields.Selection([('down', 'Down'), ('active', 'Activo'),
                              ('disconnected', 'Disconnected')],
                             string='Estado Radius', default='down')
    core_state = fields.Selection([('down', 'Down'), ('active', 'Activo'),
                              ('disconnected', 'Disconnected')],
                             string='Estado Core', default='down')

    wan_state = fields.Selection([('connected', 'Conectado'), ('disconnected', 'Desconectado'), ('none', '')], string="Estado WAN", default='none')

    changed_onu = fields.Boolean(string="ONU Cambiada", default=False)
    old_onu_pon_id = fields.Integer(string="ONU id vieja", default=0)

    discovered_onu_id = fields.Many2one(
        'silver.olt.discovered.onu',
        string='ONU Descubierta',
        help="Seleccione una ONU de la lista de equipos descubiertos por la OLT."
    )

    temp_onu_serial_display = fields.Char(string="Serial ONU Seleccionado", readonly=True)

    @api.onchange('ip_address_id')
    def _onchange_ip_address_id(self):
        if self._origin.ip_address_id and (self._origin.ip_address_id.contract_id.id == self.id):
            self._origin.ip_address_id.contract_id = None
        self.ip_address_id.contract_id = self.id

    @api.depends('olt_port_id', 'onu_pon_id', 'state')
    def _computonupon(self):
        for r in self:
            r.onupon =  f"{r.olt_port_id,r.onu_pon_id}" if r.state in ['active', 'open'] else None

    @api.depends('ip_address_ids')
    def _compute_ip_address_count(self):
        for rec in self:
            rec.ip_address_count = len(rec.ip_address_ids)

    @api.onchange('discovered_onu_id')
    def _onchange_discovered_onu_id(self):
        """
        Al seleccionar una ONU descubierta, llama al método centralizado para obtener
        los valores y actualiza el formulario.
        """
        for s in self:
            if s.discovered_onu_id:
                vals = s._prepare_contract_values_from_onu(s.discovered_onu_id)
                s.update(vals)
            else:
                # Opcional: limpiar los campos si se deselecciona la ONU
                s.update({
                    'temp_onu_serial_display': False,
                    'serial_number': False,
                    'hardware_model_id': False,
                    #'model_name': False,
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
        Model = self.env['silver.hardware.model']



        serial_number = discovered_onu.serial_number
        olt_index = discovered_onu.olt_index

        # --- Buscar o crear Lote/Serial ---
        lot = StockLot.search([('name', '=', serial_number)], limit=1)
        #model = Model.search([('name', '=', discovered_onu.model)], limit=1)
        #if (not model) or (not len(model)):
        #    model = Model.create({ 'name': discovered_onu.model})

        print(("es modelo", discovered_onu.hardware_model_id))

        if not lot:
            lot = StockLot.create({
                'name': serial_number,
                'hardware_model_id': discovered_onu.hardware_model_id.id,
                'brand_id': discovered_onu.hardware_model_id.brand_id.id,
               # 'model_name': discovered_onu.model_name,
                'product_id': None,
                'external_equipment': True,
                'software_version': discovered_onu.version,
                'company_id': self.company_id.id or self.env.company.id,
            })

        print(("lot", lot, self.olt_id))

        # --- Parsear olt_index y buscar/crear Tarjeta y Puerto ---
        card = None
        port = None
        #onu_pon_id = None
        if olt_index and 'GPON' in olt_index and self.olt_id:
            try:
                clean_index = olt_index.replace('GPON', '')
                card_str, port_pon_str = clean_index.split('/')
                port_str, pon_id_str = port_pon_str.split(':')

                card_index = int(card_str)
                port_index = int(port_str)



                #onu_pon_id = int(pon_id_str)

                card = OltCard.search([('olt_id', '=', self.olt_id.id), ('num_card', '=', card_index)], limit=1)
                print(("card",card, self.olt_id.id, card_index, olt_index))
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
            'discovered_onu_id' : discovered_onu,
            'temp_onu_serial_display': serial_number,
            'serial_number': serial_number,
            'hardware_model_id': discovered_onu.hardware_model_id,
            #'model_name': discovered_onu.model_name,
            'stock_lot_id': lot.id,
            'olt_card_id': card.id if card else False,
            'olt_port_id': port.id if port else False,
      #      'onu_pon_id': onu_pon_id,
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





    @api.onchange('partner_id')
    def onchange_partner_id(self):

        print("chpartner")

        for a in self:
            if not a.partner_id: continue
            if not a.partner_id.vat:
                raise UserError(_("Cliente no tiene identificación"))

            a.pppoe_password = a.partner_id.vat



            if not a.wifi_line_ids:


                default_lines = [
                    (0, 0, {
                        'ssid_index': 1,
                        'name': a.partner_id.name.split(" ")[0]+'-5G',
                        'password': max(a.partner_id.vat.split("-"), key=len),
                    }),
                    (0, 0, {
                        'ssid_index': 5,
                        'name': a.partner_id.name.split(" ")[0],
                        'password': max(a.partner_id.vat.split("-"), key=len),
                    }),
                ]
                # Añadirlas al diccionario de valores de creación
                a.wifi_line_ids = default_lines





    def create(self, vals):
        new_contract = super(IspContract, self).create(vals)
        if new_contract.discovered_onu_id:
            new_contract.discovered_onu_id.write({'contract_id': new_contract.id})
        if new_contract.ip_address_id:
            new_contract.ip_address_id.write({'contract_id': new_contract.id})

        return new_contract

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
    #brand_name = fields.Char(string='Marca ONU', related='stock_lot_id.brand_name', readonly=True, store=False)
    #model_name = fields.Char(string='Modelo ONU', related='stock_lot_id.model_name', readonly=True, store=False)
    brand_id = fields.Many2one('product.brand', string="Marca", related='stock_lot_id.brand_id', readonly=True, store=True)
    brand_logo = fields.Binary(related='brand_id.logo', string='Logo de la Marca')
    hardware_model_id = fields.Many2one('silver.hardware.model', string='Modelo', related='stock_lot_id.hardware_model_id', readonly=True, store=True)

    profile_id = fields.Many2one('silver.onu.profile', string='Perfil ONU', related='stock_lot_id.hardware_model_id.onu_profile_id', readonly=True, store=False)
    software_version = fields.Char(string='Versión de Software ONU', related='stock_lot_id.software_version', readonly=True, store=False)

    firmware_version = fields.Char(string='Firmware Version ONU', related='stock_lot_id.firmware_version', readonly=True, store=False)
    serial_number = fields.Char(string='Serial ONU', related='stock_lot_id.serial_number', readonly=True, store=False)
    mac_address_onu = fields.Char(string="MAC Address ONU", related='stock_lot_id.mac_address', readonly=True, store=False)

    manual = fields.Boolean(string="Configuración Manual", related='stock_lot_id.manual', readonly=True, store=False)

    # --- Campos de Estado de Aprovisionamiento ---
    wan_config_successful = fields.Boolean(string="Configuración WAN Exitosa", default=False, readonly=True, copy=False)
    wifi_config_successful = fields.Boolean(string="Configuración WiFi Exitosa", default=False, readonly=True, copy=False)

    def action_add_radius_access(self):
        def tom(p):
            if p<0.001: return "0"
            r = f"{p}".strip("0").strip(".")
            if not r: return "0"
            return f"{r}M"

        """
        Crea o actualiza el usuario en el User Manager del RADIUS server asociado,
        incluyendo la IP asignada y el perfil de velocidad detallado.
        """
        self.ensure_one()
        
        if not self.core_id:
            raise UserError(_("No tiene un core configurado."))
        
        radius_id = self.core_id.radius_id or self.core_id
        if not radius_id:
            raise UserError(_("Este contrato no tiene un servidor RADIUS asociado."))
        
        if not self.pppoe_user or not self.pppoe_password:
            raise UserError(_("Se requiere un usuario y contraseña PPPoE en el contrato."))

        # --- Construcción de Parámetros Adicionales ---
        ip_address = self.ip_address_id.name if self.ip_address_id else None
        rate_limit_str = None

        # Buscar el producto de servicio principal en las líneas del contrato
        service_product = self.line_ids.filtered(lambda l: l.product_id.service_type_id.code == 'internet')[:1].product_id
        
        if service_product:
            # Construir el string de Mikrotik-Rate-Limit
            # Formato: rx-rate[/tx-rate] [rx-burst-rate[/tx-burst-rate] [rx-burst-threshold[/tx-burst-threshold] [rx-burst-time[/tx-burst-time] [priority] [rx-rate-min[/tx-rate-min]]]]]
            # Ejemplo: 1M/10M 2M/20M 1500k/15M 10/10 8 512k/1M
            p = service_product.product_tmpl_id
            rate_limit_str = f"{tom(p.upload_bandwidth)}/{tom(p.download_bandwidth)} {tom(p.burst_limit_upload)}/{tom(p.burst_limit_download)} {tom(p.burst_threshold_upload)}/{tom(p.burst_threshold_download)} {p.burst_time_upload}/{p.burst_time_download} {p.queue_priority} {tom(p.min_upload_bandwidth)}/{tom(p.min_download_bandwidth)}"
            


        # --- Llamada a la función centralizada ---
        result = radius_id.create_user_manager_user(
            username=self.pppoe_user,
            password=self.pppoe_password,
            customer=self.partner_id.name,
            ip_address=ip_address,
            rate_limit=rate_limit_str
        )

        if result.get('success'):
            if self.radius_state != 'active':
                self.radius_state = 'active'
                # No retornar notificación si solo fue un cambio de estado para no ser muy verboso
                return True
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Éxito'),
                    'message': result.get('message'),
                    'type': 'success',
                }
            }
        else:
            cambio = self.radius_state != 'down'
            self.radius_state = 'down'

            if cambio:

                return True
            # Si la función falla, muestra el mensaje de error que retorna
            raise UserError(result.get('message'))

    def action_check_radius_connection(self):
        """
        Verifica y configura el Core asociado como un cliente NAS en el servidor RADIUS.
        Utiliza la función centralizada en el modelo silver.core.
        """
        self.ensure_one()
        if not self.core_id:
            raise UserError(_("Este contrato no tiene un Core Router asociado."))

        # Llama a la función en silver.core y retorna su resultado (una acción de notificación)
        si = self.core_id.check_and_configure_nas(username = self.pppoe_user, password = self.pppoe_password)
        if (si != (self.core_state == 'active')):
            self.core_state = ('active' if si else 'down')
            return True
        if si:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Éxito'),
                    'message': f"Conectado al core con usuario {self.pppoe_user}",
                    'type': 'success',
                }
            }
        raise UserError(_("No se puede autenticar con el core."))


    def action_provision_base(self):
        """
        Acción para ejecutar el aprovisionamiento base, activar el contrato,
        y luego intentar las configuraciones de WAN y WiFi sin fallar.
        """
        self.ensure_one()
        if not self.core_id:
            raise UserError(_("Debe seleccionar un Core Router antes de aprovisionar el servicio."))
        #self.name = self.env['ir.sequence'].next_by_code('silver.contract.sequence')

        if self.link_type == 'fiber' and self.olt_id:
            try:
                self.olt_id.terminate_onu(self)
            except:
                pass
            # 1. Ejecutar el aprovisionamiento base. Este paso es crítico.
            self.olt_id.provision_onu_base(self)
            
            # 2. Si la base fue exitosa, activar el servicio en Odoo.
            self.write({
             #   'olt_state': 'waiting',
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
            ya = self.wan_config_successful
            self.write({'wan_config_successful': True})


            if (not ya): return True

        return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': 'Success',
            'message': 'WAN configurada',
            'type': 'success',
        }

    }
   #     return True

    def action_provision_wifi(self):
        """Acción para ejecutar la configuración WiFi."""
        self.ensure_one()
        if self.link_type == 'fiber' and self.olt_id:
            r = self.olt_id.provision_onu_wifi(self)
            print((" wifi", r))
            ya = self.wifi_config_successful
            self.write({'wifi_config_successful': True})
            if (not ya): return True
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'WI-FI configurada',
                    'type': 'success',
                }
            }
        #return True

    def write(self, vals):
        print(("write1", vals))
        # Si se modifican las líneas de WiFi, reseteamos el flag de éxito.
        if 'wifi_line_ids' in vals:
            vals['wifi_config_successful'] = False

        # Guardar la ONU original antes de que se realice el cambio
        old_onu_map = {rec.id: rec.discovered_onu_id for rec in self if 'discovered_onu_id' in vals}
        old_ip_map = {rec.id: rec.ip_address_id for rec in self if 'ip_address_id' in vals}

        res = super(IspContract, self).write(vals)

        # Después de escribir, 'self' se actualiza con los nuevos valores.
        # Iterar a través de los contratos que fueron modificados.
        for contract in self:
            if contract.id in old_ip_map:
                old_ip = old_ip_map[contract.id]
                new_ip = contract.ip_address_id

                # Desvincular la ONU antigua si es diferente de la nueva
                if old_ip and old_ip != new_ip:
                    old_ip.write({'contract_id': False})

                # Vincular la nueva ONU
                if new_ip:
                    # También es seguro reescribir si la ONU es la misma, asegura consistencia
                    new_ip.write({'contract_id': contract.id})


            if contract.id in old_onu_map:
                old_onu = old_onu_map[contract.id]
                new_onu = contract.discovered_onu_id

                # Desvincular la ONU antigua si es diferente de la nueva
                if old_onu and old_onu != new_onu:
                    old_onu.write({'contract_id': False})

                # Vincular la nueva ONU
                if new_onu:
                    # También es seguro reescribir si la ONU es la misma, asegura consistencia
                    new_onu.write({'contract_id': contract.id})


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
                        commands.append(f"ont ipconfig {contract.olt_port_id.name} {contract.onu_pon_id} ip-index 1 dhcp-enable enable vlan-id {contract.vlan_id.vlanid}")
                        commands.append(f"ont wan {contract.olt_port_id.name} {contract.onu_pon_id} ip-index 1 mode bridge")

                    elif not contract.is_bridge:
                        # Modo Router (asumimos PPPoE si hay credenciales)
                        if contract.pppoe_user and contract.pppoe_password:
                            commands.append(f"ont ipconfig {contract.olt_port_id.name} {contract.onu_pon_id} ip-index 1 pppoe-enable enable username {contract.pppoe_user} password {contract.pppoe_password} vlan-id {contract.vlan_id.name or olt.vlan_id.name}")
                            commands.append(f"ont wan {contract.olt_port_id.name} {contract.onu_pon_id} ip-index 1 mode pppoe")

                # --- 2. Gestión de Cambio de Plan (Ancho de Banda) ---
                if 'product_id' in vals and olt.is_control_traffic_profile:
                    new_product = self.env['product.product'].browse(vals['product_id'])
                    # Asumimos que el product.template tiene una referencia al perfil de tráfico
                    if new_product and hasattr(new_product, 'traffic_profile_id') and new_product.traffic_profile_id:
                        tprofile_name = new_product.traffic_profile_id.name
                        commands.append(f"ont traffic-profile {contract.olt_port_id.name} {contract.onu_pon_id} profile-name {tprofile_name}")

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
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': _('Advertencia'),
                                'message': f"La OLT {olt.name} no tiene un dispositivo de red configurado.",
                                'type': 'warning',
                            }
                        }
                        continue

                    try:
                        with netdev._get_olt_connection() as conn:
                            for command in full_sequence:
                                success, response, output = conn.execute_command(command)
                                if not success:
                                    return {
                                        'type': 'ir.actions.client',
                                        'tag': 'display_notification',
                                        'params': {
                                            'title': _('Error de OLT'),
                                            'message': f"Un comando falló en la OLT para el contrato {contract.name}.\nComando: {command}\nError: {output}",
                                            'type': 'warning',
                                        }
                                    }

                    except Exception as e:
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': _('Error de Conexión OLT'),
                                'message': f"No se pudo conectar a la OLT para actualizar el contrato {contract.name}.\nError: {e}",
                                'type': 'warning',
                            }
                        }
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
                'state_service': 'suspended',
                'date_cut': fields.Date.context_today(self)
            })
            return True
        return super(IspContract, self).action_cutoff_service()

    def action_reconnection_service_button(self):
        self.ensure_one()
        if not self.core_id:
            raise UserError(_("Debe seleccionar un Core Router antes de aprovisionar el servicio."))

        if self.link_type == 'fiber' and self.olt_id:
            print(("aa", self.state_service, self.changed_onu))
            if (self.state_service != 'suspended' ) or (self.changed_onu) :
                self.changed_onu = False
                print(("bb", self.state_service, self.old_onu_pon_id))
                #if (self.old_onu_pon_id and (self.old_onu_pon_id != self.onu_pon_id)):
                try:
                    self.olt_id.terminate_onu(self)
                except:
                    pass
                self.olt_id.provision_onu_base(self)
            else:
                self.olt_id.enable_onu(self)
        self.write({
         #   'state': 'open',
            'state_service': 'active',
            'date_reconnection': fields.Date.context_today(self)
        })
        return True
        return    {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Éxito'),
                'message': _('El servicio ha sido restaurado correctamente.'),
                'type': 'success',
            }
        }
      #  return True

    def action_suspend_service(self):
        self.ensure_one()
        if self.ip_address_id:
            self.ip_address_id.write({"contract_id":  None} )

        if self.link_type == 'fiber' and self.olt_id:
            self.olt_id.disable_onu(self)
        self.write({
            'wifi_config_successful': False,
            'wan_config_successful': False,
            'state_service': 'suspended',
            'date_reconnection': fields.Date.context_today(self)
        })
        return True
        return  {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Éxito'),
                    'message': _('El servicio ha sido suspendido  correctamente.'),
                    'type': 'success',
                }
            }
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
          #  if contract.state == 'closed':
         #       raise UserError(_("Este contrato ya ha sido dado de baja."))

            # --- Lógica de Terminación para PPPoE en Mikrotik (User Manager) ---
           # if contract.pppoe_user and contract.core_id:
             #   api = None
             #   try:
            api, e = contract.core_id._get_api_connection()
            if not api:
                raise UserError(_("Could not connect to the MikroTik router: %s") % e)
#                raise UserError(_("No se pudo conectar al Core Router Mikrotik."))

            user_path = api.path('/user-manager/user')
            name = Key("name")
            existing_user = tuple((user_path.select(Key(".id")).where(name == contract.pppoe_user)))
            #existing = tuple(user_path('print', **{'?name': contract.pppoe_user}))

            print(("existing", existing_user))

            if existing_user:
                user_path.remove(existing_user[0][".id"])


           #     except Exception as e:
            #        print("Falla core")

            #    finally:
            #        if api:
            #            api.close()

            # --- Lógica de Terminación para OLT (Fibra Óptica) ---
            if contract.link_type == 'fiber':
                self.olt_id.terminate_onu(self)


            contract.write({
                'wifi_config_successful': False,
                'wan_config_successful': False,
                #'onu_pon_id': None,
                'olt_state' : 'down',
                'core_state': 'down',
                'radius_state': 'down',
                'state_service': 'terminated',
                'ip_address_id': None,
                #'state': 'closed',
                'date_end': fields.Date.context_today(self)
            })



        return True

    def action_ping_service(self):
        self.ensure_one()
        if not self.ip_address_id or not self.ip_address_id.name:
            raise UserError(_("No hay ninguna dirección IP asignada a este contrato para hacer ping."))
        if not self.core_id:
            raise UserError(_("No se ha configurado un router principal (Core) para ejecutar el ping."))

        ping_result_str = ""
        try:
            api,e = self.core_id._get_api_connection()
            if not api:
                raise UserError(_("Could not connect to the MikroTik router: %s")%e)
            
            try:
                # El comando ping en la API de Mikrotik devuelve un iterador.
                ping_results = api(cmd='/ping', address=self.ip_address_id.name, count='5')
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



    def action_contract_reset_onu(self):
        self.ensure_one()
        if self.link_type == 'fiber' and self.olt_id:
            self.olt_id.reset_onu(self)
            return True
        raise UserError("Función no implementada para este tipo de conexión.")

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

    def action_view_pppoe_traffic_chart(self):
        """
        Se conecta al Core, busca la sesión PPPoE activa por la dirección IP del contrato y,
        si la encuentra, lanza un asistente para mostrar el gráfico de la interfaz correspondiente.
        """
        self.ensure_one()

        if not self.core_id:
            raise UserError(_("Este contrato no tiene un Core Router asociado."))
        if not self.ip_address_id or not self.ip_address_id.name:
            raise UserError(_("Este contrato no tiene una dirección IP asignada para buscar la sesión."))

        api = None
        if 1:
       # try:
            netdev = self.core_id#.netdev_id
            if not netdev:
                raise UserError(_("El Core Router no tiene un dispositivo de red configurado para la conexión."))
            
            api, e = netdev._get_api_connection()
            if not api:
                raise UserError(_("Could not connect to the MikroTik router: %s")%e)

            assigned_ip = self.ip_address_id.name
            #ppp_active_path = api.path('/ppp/active')

            ppp_active = api.path('/ppp/active')

            #for ppp in ppp_active:
            # Buscar la conexión activa usando la IP asignada en el campo 'address'
            #ppp_active_path
            #active_connections = tuple(ppp_active_path.select(Key("interface")))


            #   print(("active", ppp))
            #active_connections = []

            active_connections = ppp_active.select(Key("name"), Key("service"), Key("caller-id"), Key("address"), Key("uptime")).where(Key("address") == assigned_ip)

          #  print(("active", ppp, tuple(active_connections)))

            if not active_connections:
                raise UserError(_("No se encontró una sesión PPPoE activa para la dirección IP '%s'.") % assigned_ip)

            wizard = self.env['silver.netdev.ppp.active.wizard'].create({'router_id': self.core_id.id})
            for ppp in active_connections:
                r = self.env['silver.netdev.ppp.active.wizard.line'].create({
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
                        'default_netdev_id': self.core_id.netdev_id.id,
                    }
                }

            try:
                interface_name = tuple(active_connections)[0]['name']
            except:
                 raise UserError(_("Error en sesión PPPoE para la dirección IP '%s'.") % assigned_ip)

            wizard = self.env['silver.contract.traffic.wizard'].create({
                'core_id': self.core_id.id,
                'interface': interface_name,
            })

            return {
                'name': _('Gráfico de Tráfico en Tiempo Real'),
                'type': 'ir.actions.act_window',
                'res_model': 'silver.contract.traffic.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('silver_provisioning.view_silver_contract_traffic_wizard_form_chart_only').id,
                'res_id': wizard.id,
                'target': 'new',
            }

        #except Exception as e:
        #    raise UserError(_("Se produjo un error: %s") % e)
        #finally:
         #   if api:
         #       api.close()

    @api.onchange('onu_pon_id')
    def _onchange_onu_pon_id(self):
        self.changed_onu = True
        if self._origin:
            self.old_onu_pon_id = self._origin.onu_pon_id
        print(("changed", self.old_onu_pon_id, self.changed_onu))

    #@api.onchange('olt_id')
    #def _onchange_olt_id(self):
      #  self.changed_onu = True
      #  self.vlan_id = self.olt_id.vlan_id

    @api.onchange('stock_lot_id')
    def _onchange_stock_lot_id(self):
        self.changed_onu = True


    @api.onchange('olt_port_id', 'core_id')
    def _onchange_olt_port_core_id(self):
        def filterip(ip):
            print(("fip", ip.id, self.ip_address_id.id))
            return ip.id != self.ip_address_id.id

        card_index = self.olt_port_id.olt_card_id.num_card
        port_index = self.olt_port_id.num_port

        # 1. Búsqueda Local en Contratos
        local_found = False
        if self.olt_port_id:
            # Buscar IDs usados en contratos existentes para este puerto
            used_ids = self.env['silver.contract'].search([
                ('olt_port_id', '=', self.olt_port_id.id),
                ('id', '!=', self._origin.id) # Excluirse a sí mismo si ya existe
            ]).mapped('onu_pon_id')
            
            used_set = set()
            for uid in used_ids:
                try:
                    used_set.add(int(uid))
                except (ValueError, TypeError):
                    pass

            for i in range(1, 129):
                if i not in used_set:
                    self.onu_pon_id = i
                    local_found = True
                    print(f"Found local free ONU ID: {i}")
                    break
        
        # 2. Fallback a OLT si no se encontró localmente (o si se prefiere verificar siempre)
        # La instrucción dice "antes de buscar en...", implicando que si se encuentra, no se busca fuera.
       # if not local_found:
        try:
            self.onu_pon_id = int(self.olt_id.get_next_free_onu_id(f"{card_index}/{port_index}") or "1")
            print(("ponid", card_index, port_index, self.onu_pon_id))
        except Exception as e:
            print(("error en pon", card_index, port_index))

        if self.link_type=='wifi':
            self.changed_onu = True
            self.vlan_id = self.env['silver.vlan'].search([(self.olt_id, 'in', 'olt_ids')], limit=1)


        # Asignación de IP
        available_ips = []
        if self.olt_port_id:
            # Buscar pools de IPs asociados a este puerto OLT
            available_ips = self.env['silver.ip.address'].search([('olt_port_id', '=', self.olt_port_id.id),
                                                                  ('public', '=', False),
                                                                  '|', ('contract_id', '=', False), ('contract_id', '=', self.id)
                                                             ], order='ip_int asc')  # Ordenar por IP numericamente

        print(("ips1", available_ips))
        if (not available_ips) and (not len(available_ips)):
            available_ips = self.env['silver.ip.address'].search([('olt_id', '=', self.olt_id.id), ('olt_port_id', '=', None),
                                                                  ('public', '=', False),
                                                                  '|', ('contract_id', '=', False), ('contract_id', '=', self.id)
            ], order='ip_int asc') # Ordenar por IP numericamente

        print(("ips2", available_ips))
        if (not available_ips) and (not len(available_ips)):
            available_ips = self.env['silver.ip.address'].search([('core_id', '=', self.core_id.id),
                                                                  ('public', '=', False),
                                                                  '|', ('contract_id', '=', False),
                                                                  ('contract_id', '=', self.id)
            ], order='ip_int asc') # Ordenar por IP numericamente

        print(("ips3", available_ips))

        public_ips = self.env['silver.ip.address'].search([ ('public', '=', True),
                                                            '|', '|', ('zone_ids', 'in', self.node_id.zone_id.id),
                                                            ('node_ids', 'in', self.node_id.id), ('core_ids', 'in', self.core_id.id)  ] )

        #dicips1 = {}
        #for a in available_ips:
        #    dicips1[a.name] = a
        #dicips2 = {}
        #for a in public_ips:
        #    dicips2[a.name] = a


        # Store the current ip_address_ids
        #current_ips = self.ip_address_ids

        #print(("ips", available_ips, current_ips, len(available_ips), len(tuple(available_ips))))

        # Remove the currently selected IP from the list if it exists

        #current_ips1 = (current_ips.filtered(lambda ip: dicips1.get(ip.name)) if current_ips and len(current_ips) else current_ips)
        #current_ips2 = (current_ips.filtered(lambda ip: dicips2.get(ip.name)) if current_ips and len(current_ips) else current_ips)
        #if (((not current_ips1) or (not len(current_ips1))) and available_ips and len(tuple(available_ips))):

         #   current_ips1 = available_ips[0]


        self.ip_address_id = (available_ips[0] if (available_ips and len(available_ips)) else public_ips[0])


        #print(("ip3", current_ips.filtered(filterip) , current_ips1, current_ips2,  self.ip_address_id))

        # Prepend available_ips and then add the rest of the existing ips
        #self.ip_address_ids = current_ips1+(current_ips2)

        #self.ip_address_id = current_ips1




        self.vlan_id = False

        # Lógica de cascada para VLAN
        try:
            self.vlan_id = self.core_id.vlan_ids[0]
        except:
            pass
        try:
            self.vlan_id = self.olt_id.vlan_ids[0]
        except:
            pass
        try:
            self.vlan_id = self.olt_port_id.vlan_ids[0]
        except:
            pass

        self.changed_onu = True




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
        self.core_id = self.box_id.core_id
        self.olt_id = self.box_id.olt_id
        self.olt_port_id = self.box_id.olt_port_id


    @api.onchange('node_id')
    def _onchange_node_id(self):
        print(( "change node", self.box_id, self.node_id))
        if self.box_id and (self.box_id.node_id != self.node_id):
            self.box_id = None

    @api.onchange('wifi_line_ids')
    def _onchange_wifi_line_ids(self):
        self.wifi_config_successful = False



    def action_check_olt_state(self):
        self.ensure_one()
        if not self.olt_id or not self.onu_pon_id:
            raise UserError(_("Por favor, asegúrese de que la OLT y el ID de ONU en PON estén configurados."))

        reload_action = {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
        ostate = self.olt_state
        netdev = self.olt_id.netdev_id
        if not netdev:
            self.olt_state = 'down'
            raise UserError(_("La OLT no tiene un dispositivo de red configurado."))

        pon_port = f"{self.olt_card_id.num_card or self.olt_port_id.olt_card_id.num_card}/{self.olt_port_id.num_port}"

        commands = [
            f"configure terminal",
            f"interface gpon {pon_port}",
            f"show onu info {self.onu_pon_id}",
            f"onu  {self.onu_pon_id} pri wan_conn show",
            f"onu {self.onu_pon_id} pri wan_adv commit",
        ]

        try:
        #if 1:
            old1 = self.olt_state
            old2 = self.wan_state
            with netdev._get_olt_connection() as conn:
                full_output = ""
                for command in commands:
                    success, response, output = conn.execute_command(command)
                    full_output += output

                    if "wan_adv commit" in command:
                        continue

                    if 'show onu' in command:
                        print(("show onu", full_output))
                        if "Onuindex" in full_output and "Profile" in full_output :
                            self.olt_state = 'active'
                        else:
                            self.olt_state = 'down'
                            break

                    if ("pri wan" in command):
                        #self.olt_state = 'down'
                        self.wan_state = 'none'

                        if "wanIndex" in full_output and "PPPOE" in full_output:
                            self.olt_state = 'active'
                            # Extraer wanStatus
                            wan_status_match = re.search(r"wanStatus\s*:\s*(\w+)", full_output)
                            print(("wan_status_noextracted", wan_status_match))
                            cambio = False
                            if wan_status_match:
                                wan_status = wan_status_match.group(1).lower()
                                print(("wan_status_extracted", wan_status))

                                if wan_status in ['connected', 'disconnected']:
                                    self.wan_state = wan_status

                if self.olt_state != old1 or self.wan_state != old2:
                    return True

                if self.olt_state == 'down':
                    raise UserError(_("La ONU no parece estar conectada o no se encontró información."))

                s = full_output.strip().split('\n')[-1]
                message = f"Información de la ONU:\n{s}"
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('ONU Conectada'),
                        'message': message,
                        'type': 'success',
                    }
                }


        except Exception as e:
            self.olt_state = 'down'
            if self.olt_state != old1 or self.wan_state != old2:
                return True
            return [{
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'sticky': False,
                    'message': f'Conexión a la OLT falla: {e}',
                    'type': 'warning',
                }
            }, reload_action]
            # Usar notify_warning para no bloquear al usuario con un UserError si la conexión falla
        #    self.env.user.notify_warning(
        #        message=f"No se pudo conectar a la OLT o verificar el estado de la ONU.\nError: {e}"
        #    )
        
        return True

    # La función clave: Transforma el texto crudo en HTML
    def _format_data_to_html(self, raw_text):
        if not raw_text:
            return ""

        # Divide las líneas y filtra las líneas de encabezado (las que tienen '***')
        lines = [line.strip() for line in raw_text.split("\n") if line.strip() and '***' not in line]

        html_content = "<div class='wan-data-table'>"
        html_table = "<table class='table table-sm table-borderless'>"


        for line in lines:
            if ':' in line:
                # Divide solo por la primera ocurrencia de ':'
                key, value = line.split(':', 1)

                # Agrega una fila a la tabla
                html_table += f"""
                    <tr>
                        <td class='wan-key'>{key.strip()}</td>
                        <td class='wan-value'>{value.strip()}</td>
                    </tr>
                """
            else:
                # Maneja el encabezado o líneas que no tienen ':' (como nwanNumber)
                html_table += f"<tr class='wan-separator-row'><td><strong>{line}</strong></td></tr>"

        html_table += "</table>"

        print(("html", html_table))
        return html_table

    def _format_dict_to_html(self, data_dict):
        """
        Helper function to format a dictionary into a simple HTML table.
        Reuses the same styling as _format_data_to_html.
        """
        if not data_dict:
            return ""

        html_table = "<table class='table table-sm table-borderless'>"
        for key, value in data_dict.items():
            # Clean up the key name (e.g., '.id' -> 'ID')
            clean_key = key.replace('.', '').replace('-', ' ').title()
            html_table += f"""
                <tr>
                    <td class='wan-key'>{clean_key}</td>
                    <td class='wan-value'>{value}</td>
                </tr>
            """
        html_table += "</table>"
        return html_table

    def get_radius_user_info(self):
        """
        Connects to the User Manager on the RADIUS server and retrieves
        information about the user and their active sessions.
        """
        self.ensure_one()

        if not self.core_id:
            raise UserError(_("No tiene un core configurado para consultar el RADIUS."))
        
        radius_server = self.core_id.radius_id or self.core_id
        if not radius_server:
            raise UserError(_("El core no tiene un servidor RADIUS (User Manager) asociado."))
            
        if not self.pppoe_user:
            raise UserError(_("No hay un usuario PPPoE definido en el contrato."))

        netdev = radius_server#.netdev_id
        if not netdev:
            raise UserError(_("El servidor RADIUS no tiene un dispositivo de red (netdev) configurado para la conexión."))

        user_info_html = "<h3>Usuario no encontrado</h3>"
        session_info_html = "<h3>No hay sesiones activas</h3>"
        api = None

       # try:
        if 1:
            api,e = netdev._get_api_connection()
            if not api:
                raise UserError(_("Could not connect to the MikroTik router: %s")%e)

            # --- Get User Info ---
            user_path = api.path('/user-manager/user')
            user_data = tuple(user_path.select().where(Key('name') == self.pppoe_user))

            print(("udata", user_data))


            if user_data:
                # user_data is a tuple of dicts, we want the first one
                user_info_html = "<h3>Detalles del Usuario</h3>" + self._format_dict_to_html(user_data[0])

            start_of_last_month = datetime.now().replace(day=1, hour=0, minute=0, second=0,
                                                         microsecond=0) - relativedelta(months=1)

            # 2. Fin: Primer día del mes actual a las 00:00:00 (que es el límite superior 'menor que')
            start_of_this_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            # El formato que Mikrotik usa típicamente es "MMM/DD/YYYY HH:MM:SS"
            # Ejemplo: "Nov/27/2025 00:00:00"
            start_date_str = start_of_last_month.strftime("%b/%d/%Y %H:%M:%S")
            end_date_str = start_of_this_month.strftime("%b/%d/%Y %H:%M:%S")

            # --- Get Session Info ---
            #session_path = api.path('/user-manager/session')
            #session_data = tuple(session_path.select().where(Key('user') == self.pppoe_user,
            #                                                 Key('start-time') > start_date_str,
            #                                                 # Nota: el ' ' después de > es crucial
            #                                                 # 2. Que el tiempo de inicio sea MENOR que el inicio del mes actual
            #                                                 Key('start-time') < end_date_str
            #                                                 ))
            session_data = None
            print(("sdata", session_data))

            if session_data:
                session_info_html = "<h3>Sesiones Activas</h3>"
                for session in session_data:
                    session_info_html += self._format_dict_to_html(session) + "<hr/>"

        #except Exception as e:
        #    raise UserError(_("Error al consultar el User Manager: %s") % e)
        #finally:
            if api:
                api.close()
                
        full_html = user_info_html + "<br/>" + session_info_html

        wizard = self.env['silver.display.info.wizard'].create({
            'info': full_html,
        })

        return {
            'name': _('Información de Usuario RADIUS'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.display.info.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def button_get_wan_info(self):
        self.ensure_one()

        info_str = ""
        if not self.olt_id or not self.onu_pon_id:
            raise UserError(_("Por favor, asegúrese de que la OLT y el ID de ONU en PON estén configurados."))

        netdev = self.olt_id.netdev_id
        if not netdev:
            raise UserError(_("La OLT no tiene un dispositivo de red configurado."))
        pon_port = f"{self.olt_card_id.num_card or self.olt_port_id.olt_card_id.num_card}/{self.olt_port_id.num_port}"

        commands = [
            f"configure terminal",
            f"interface gpon {pon_port}",
            f"show onu {self.onu_pon_id} pri wan_adv"
        ]

        try:
            with netdev._get_olt_connection() as conn:
                # No es necesario entrar en 'configure terminal' o 'interface gpon' para este comando
                # ya que 'show onu X pri wan_adv' es un comando de nivel superior en algunas OLTs.
                # Si la OLT requiere un contexto específico, se debería ajustar aquí.
                full_output = ""
                for command in commands:
                    success, response, output = conn.execute_command(command)
                    full_output += output

                self.wan_state = 'none'
                wan_status_match = re.search(r"wanStatus\s*:\s*(\w+)", full_output)
                if wan_status_match:
                    wan_status = wan_status_match.group(1).lower()
                    print(("wan_status_extracted", wan_status))
                    if wan_status in ['connected', 'disconnected']:
                        self.wan_state = wan_status


                #if success:

                info_str = self._format_data_to_html(output)
                print(("outpuuuu", output, info_str))
            #else:
            #    return {
            ##        'type': 'ir.actions.client',
            #       'tag': 'display_notification',
            #        'params': {
            #            'title': _('Error de Información WAN'),
            #            'message': info_str,
            #            'type': 'warning',
            #        }
            #    }

        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error de Conexión OLT'),
                    'message': info_str,
                    'type': 'warning',
                }
            }

        wizard = self.env['silver.display.info.wizard'].create({
            'info': info_str,
        })

        return {
            'name': _('Información WAN de ONU'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.display.info.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }
    def button_get_wifi_info(self):
        self.ensure_one()

        info_str = ""
        if not self.olt_id or not self.onu_pon_id:
            raise UserError(_("Por favor, asegúrese de que la OLT y el ID de ONU en PON estén configurados."))

        netdev = self.olt_id.netdev_id
        if not netdev:
            raise UserError(_("La OLT no tiene un dispositivo de red configurado."))

        pon_port = f"{self.olt_card_id.num_card or self.olt_port_id.olt_card_id.num_card}/{self.olt_port_id.num_port}"

        commands = [
            f"configure terminal",
            f"interface gpon {pon_port}",
            #f"show onu {self.onu_pon_id} pri wan_adv"
        ]
        for a in range(1, 9):
            commands.append(f"show onu {self.onu_pon_id} pri wifi_ssid {a}")

        info_str = ''

        try:
            with netdev._get_olt_connection() as conn:
                #success, full_output, clean_response = conn.execute_command(f"show onu {self.onu_pon_id} pri wifi_ssid 1")
                full_output = ""

                for command in commands:
                    success, response, output = conn.execute_command(command)
                    full_output += output
                    if ('SSID' in output) and ( 'Enable' in output):
                        info_str += output+ " \n"
                


        except Exception as e:
            info_str = _(f"No se pudo conectar a la OLT para obtener información WiFi.\nError: {e}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error de Conexión OLT'),
                    'message': info_str,
                    'type': 'warning',
                }
            }

        wizard = self.env['silver.display.info.wizard'].create({
            'info': self._format_data_to_html(info_str),
        })

        return {
            'name': _('Información WiFi de ONU'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.display.info.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }
