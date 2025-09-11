# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class IspContract(models.Model):
    _name = 'isp.contract'
    _description = 'Contrato de Servicio ISP'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Campos de Cabecera y Cliente
    name = fields.Char(string="Número de Contrato", required=True, copy=False, readonly=True, default=lambda self: _('Nuevo'))
    partner_id = fields.Many2one('res.partner', string="Cliente", required=True, tracking=True)

    address = fields.Char(string="Dirección de Instalación", required=True)
    phone = fields.Char(string="Teléfono", related='partner_id.phone', readonly=False)

    date_start = fields.Date(string="Fecha de Inicio", default=fields.Date.context_today, tracking=True)
    date_end = fields.Date(string="Fecha de Fin", tracking=True)

    # Campos de Configuración
    payment_type_id = fields.Many2one('isp.payment.type', string="Forma de Pago")
    service_type_id = fields.Many2one('isp.service.type', string="Tipo de Servicio", required=True)
    plan_type_id = fields.Many2one('isp.plan.type', string="Tipo de Plan", required=True)
    contract_term_id = fields.Many2one('isp.contract.term', string="Período de Permanencia")
    cutoff_day_id = fields.Many2one('isp.cutoff.day', string="Día de Corte")
    tag_ids = fields.Many2many('isp.contract.tag', string="Etiquetas")  # TODO: Crear modelo isp.contract.tag

    # Campos de Servicio (reemplazan a los anteriores)
    service_plan_id = fields.Many2one('product.product', string="Plan de Servicio", required=True, domain="[('is_isp_plan', '=', True)]")
    monthly_fee = fields.Float(string="Tarifa Mensual", related='service_plan_id.list_price', readonly=False)


    state = fields.Selection([
        ('draft', 'Borrador'), ('open', 'En Proceso'), ('done', 'Realizado'),
        ('cancel', 'Cancelado'), ('renewal', 'Renovación'),
    ], string="Estado", default='draft', tracking=True)
    state_service = fields.Selection([
        ('inactive', 'Inactivo'), ('active', 'Activo'), ('disabled', 'Cortado'),
        ('suspended', 'Suspendido'), ('removal_list', 'En Lista de Retiro'), ('removed', 'Retirado'),
    ], string="Estado del Servicio", default='inactive', tracking=True)

    # --- Pestaña: Servicios Recurrentes ---
    line_ids = fields.One2many('isp.contract.line', 'contract_id', string='Líneas de Servicio Recurrente', domain=[('line_type', '=', 'recurring')])
    line_debit_ids = fields.One2many('isp.contract.line', 'contract_id', string='Líneas de Cargo Único', domain=[('line_type', '=', 'one_time')])
    payment_type_id = fields.Many2one('isp.payment.type', string="Forma de Pago")
    date_start = fields.Date(string="Fecha de Inicio", default=fields.Date.context_today, tracking=True)
    date_end = fields.Date(string="Fecha de Fin", tracking=True)

    # --- Pestaña: Descuentos/Promociones ---
    discount_plan_id = fields.Many2one('isp.discount.plan', string="Plan de Descuento")
    discount_line_ids = fields.One2many('isp.contract.discount.line', 'contract_id', string='Líneas de Descuento')
    stock_line_ids = fields.One2many('isp.contract.stock.line', 'contract_id', string='Líneas de Materiales')
    payment_promise_ids = fields.One2many('isp.payment.promise', 'contract_id', string="Promesas de Pago")
    anticipated_payment_line_ids = fields.One2many('isp.contract.anticipated.payment.line', 'contract_id', string='Líneas de Pago Anticipado')
    referred_line_ids = fields.One2many('isp.referred.contact', 'contract_id', string='Líneas de Referidos')
    # line_debit_ids = fields.One2many('isp.contract.debit.line', 'contract_id', string='Líneas de Débito/Valores Extra')

    # --- Pestaña: Ubicación ---
    street = fields.Char(string='Calle')
    street2 = fields.Char(string='Calle 2')
    city = fields.Char(string='Ciudad')
    state_id = fields.Many2one('res.country.state', string='Estado/Provincia')
    country_id = fields.Many2one('res.country', string='País')
    zip = fields.Char(string='Código Postal')
    contract_latitude = fields.Float(string='Latitud', digits=(10, 7))
    contract_longitude = fields.Float(string='Longitud', digits=(10, 7))

    # --- Pestaña: Servicio Internet ---
    link_type = fields.Selection([
        ('fiber', 'Fibra Óptica'), ('wifi', 'Inalámbrico'),
        ('lan', 'LAN'), ('fttb', 'FTTB'),
    ], string="Tipo de Conexión", default='fiber', required=True)
    node_id = fields.Many2one('isp.node', string="Nodo")
    core_id = fields.Many2one('isp.core', string="Core Router")
    ap_id = fields.Many2one('isp.ap', string="Access Point")
    splitter_id = fields.Many2one('isp.splitter', string="Splitter")
    olt_id = fields.Many2one('isp.olt', string="OLT")
    olt_port_id = fields.Many2one('isp.olt.card.port', string="Puerto OLT")
    box_id = fields.Many2one('isp.box', string="Caja (CTO)")
    port_nap = fields.Char(string="Puerto en CTO")
    onu_id = fields.Many2one('isp.netdev', string="ONU/CPE")
    serial_onu = fields.Char(string="Serial ONU")
    model_onu = fields.Char(string="Modelo ONU")
    is_bridge = fields.Boolean(string="ONU en modo Bridge")
    ip_address = fields.Char(string="Dirección IP Asignada")
    pppoe_user = fields.Char(string="Usuario PPPoE")
    pppoe_password = fields.Char(string="Contraseña PPPoE")
    mac_address_onu = fields.Char(string="MAC Address ONU")
    date_active = fields.Date(string="Fecha de Activación", readonly=True)
    date_reconnection = fields.Date(string="Fecha de Reconexión", readonly=True)
    date_cut = fields.Date(string="Fecha de Corte", readonly=True)
    date_renovation = fields.Date(string="Fecha de Renovación", readonly=True)
    sssid = fields.Char(string="SSID (Nombre WiFi)")
    password = fields.Char(string="Contraseña WiFi")
    custom_channel_id = fields.Many2one('isp.wifi.channel.line', string="Canal WiFi")
    contract_mode_wan_ids = fields.One2many('isp.contract.wan.mode', 'contract_id', string="Configuración WAN")
    new_ip_address_id = fields.Many2one('isp.ip.pool.line', string="IP de Pool")
    consumption_ids = fields.One2many('isp.contract.consumption', 'contract_id', string="Registros de Consumo")
    radius_entry_ids = fields.One2many('isp.contract.radius.entry', 'contract_id', string="Entradas de RADIUS")

    # --- Pestaña: Otra Información ---
    user_id = fields.Many2one('res.users', string='Vendedor', default=lambda self: self.env.user)
    origin = fields.Char(string="Origen Marketing")
    signature = fields.Binary(string="Firma Cliente")
    description_contract = fields.Text(string="Términos y Condiciones")
    holding_id = fields.Many2one('isp.contract.holding', string='Holding/Grupo de Contratos')
    reception_channel_id = fields.Many2one('isp.reception.channel', string='Canal de Recepción')
    tag_ids = fields.Many2many('isp.contract.tag', string="Etiquetas")

    # --- Pestaña: Documentación ---
    doc_vat_copy = fields.Binary(string="Copia de RIF/CI", attachment=True)
    installation_request = fields.Binary(string="Solicitud de Instalación", attachment=True)
    service_contract = fields.Binary(string="Contrato de Servicio Firmado", attachment=True)
    basic_service_sheet = fields.Binary(string="Ficha de Servicio Básico", attachment=True)
    is_validated = fields.Boolean(string="Documentación Validada")

    # --- Pestaña: Notificaciones ---
    is_portal_user = fields.Boolean(string="Es Usuario del Portal", compute="_compute_is_portal_user")
    dont_send_notification_wp = fields.Boolean(string="No Enviar Notificaciones por WhatsApp")
    links_payment = fields.Char(string="Enlaces de Pago", compute="_compute_links_payment", readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('isp.contract.sequence') or _('Nuevo')
        return super(IspContract, self).create(vals)

    def action_open(self): self.write({'state': 'open'})
    def action_cancel(self): self.write({'state': 'cancel'})
    def action_activate_service(self):
        for contract in self:
            # 1. Validaciones
            if not contract.line_ids:
                raise UserError(_("El contrato no tiene líneas de servicio (planes) definidos."))

            if contract.link_type == 'fiber':
                if not all([contract.olt_port_id, contract.serial_onu]):
                    raise UserError(_("Para activar un servicio de fibra, se requiere un Puerto OLT y un Serial de ONU."))
            
            elif contract.link_type == 'wifi':
                if not all([contract.ap_id, contract.mac_address_onu]):
                    raise UserError(_("Para activar un servicio inalámbrico, se requiere un AP y una MAC Address."))

            # 2. Lógica de Provisión (Plantilla a adaptar)
            try:
                # --- EJEMPLO PARA FIBRA ÓPTICA ---
                if contract.link_type == 'fiber':
                    # Asumimos que tu modelo 'isp.olt' tiene un método para provisionar
                    # Debes reemplazar 'provision_service_on_port' con el nombre real de tu función
                    # y pasar los parámetros que necesite.
                    plan = contract.line_ids[0].product_id
                    result = contract.olt_id.provision_service_on_port(
                        port=contract.olt_port_id,
                        onu_serial=contract.serial_onu,
                        customer_name=contract.partner_id.name,
                        plan_name=plan.name,
                        upload_speed=plan.upload_speed, # Asumiendo que tienes estos campos en el producto
                        download_speed=plan.download_speed # Asumiendo que tienes estos campos en el producto
                    )
                    if not result.get('success'):
                        raise UserError(_("Fallo al provisionar en la OLT: %s") % result.get('message'))

                # --- EJEMPLO PARA PPPoE (Router Core) ---
                if contract.pppoe_user and contract.core_id:
                    # Asumimos que tu modelo 'isp.core' tiene un método para crear usuarios PPPoE
                    # Debes reemplazar 'create_pppoe_user' con el nombre real de tu función
                    result = contract.core_id.create_pppoe_user(
                        username=contract.pppoe_user,
                        password=contract.pppoe_password,
                        plan_name=contract.line_ids[0].product_id.name
                    )
                    if not result.get('success'):
                        raise UserError(_("Fallo al crear el usuario PPPoE en el Core: %s") % result.get('message'))

            except Exception as e:
                raise UserError(_("Ha ocurrido un error técnico al intentar activar el servicio: %s") % e)

            # 3. Actualización de Estado
            contract.write({
                'state_service': 'active',
                'date_active': fields.Date.context_today(self)
            })
        return True
    def action_cutoff_service(self):
        for contract in self:
            if contract.state_service != 'active':
                raise UserError(_("El servicio no está activo, por lo tanto no se puede cortar."))

            # Lógica de corte de servicio (Plantilla a adaptar)
            try:
                # --- EJEMPLO PARA FIBRA ÓPTICA ---
                if contract.link_type == 'fiber' and contract.olt_port_id:
                    # Asumimos que tu modelo 'isp.olt' tiene un método para cortar el servicio
                    # Debes reemplazar 'cutoff_service_on_port' con el nombre real de tu función
                    result = contract.olt_id.cutoff_service_on_port(
                        port=contract.olt_port_id,
                        onu_serial=contract.serial_onu
                    )
                    if not result.get('success'):
                        raise UserError(_("Fallo al cortar el servicio en la OLT: %s") % result.get('message'))

                # --- EJEMPLO PARA PPPoE (Router Core) ---
                if contract.pppoe_user and contract.core_id:
                    # Asumimos que tu modelo 'isp.core' tiene un método para deshabilitar usuarios PPPoE
                    # Debes reemplazar 'disable_pppoe_user' con el nombre real de tu función
                    result = contract.core_id.disable_pppoe_user(
                        username=contract.pppoe_user
                    )
                    if not result.get('success'):
                        raise UserError(_("Fallo al deshabilitar el usuario PPPoE en el Core: %s") % result.get('message'))

            except Exception as e:
                raise UserError(_("Ha ocurrido un error técnico al intentar cortar el servicio: %s") % e)

            # Actualización de Estado
            contract.write({
                'state_service': 'disabled',
                'date_cut': fields.Date.context_today(self)
            })
        return True

    # --- Placeholder Methods ---
    def _compute_is_portal_user(self): self.is_portal_user = False
    def _compute_links_payment(self): self.links_payment = ''
    def action_register_notification(self): pass
    def action_amountdue_notification(self): pass
    def action_cutoff_notification(self): pass
    def enable_portal_access_contract(self): pass
    def disable_portal_access_contract(self): pass
    def action_reconnection_service_button(self):
        for contract in self:
            if contract.state_service not in ['disabled', 'suspended']:
                raise UserError(_("El servicio no está cortado o suspendido, por lo tanto no se puede reconectar."))

            # Lógica de reconexión de servicio (Plantilla a adaptar)
            # A menudo, la reconexión utiliza la misma lógica que la activación.
            try:
                # --- EJEMPLO PARA FIBRA ÓPTICA ---
                if contract.link_type == 'fiber' and contract.olt_port_id:
                    # Puede que sea la misma función que la de activar, o una específica para reconectar.
                    # Debes reemplazar 'reconnect_service_on_port' con el nombre real de tu función.
                    plan = contract.line_ids[0].product_id
                    result = contract.olt_id.reconnect_service_on_port(
                        port=contract.olt_port_id,
                        onu_serial=contract.serial_onu,
                        plan_name=plan.name,
                        upload_speed=plan.upload_speed,
                        download_speed=plan.download_speed
                    )
                    if not result.get('success'):
                        raise UserError(_("Fallo al reconectar el servicio en la OLT: %s") % result.get('message'))

                # --- EJEMPLO PARA PPPoE (Router Core) ---
                if contract.pppoe_user and contract.core_id:
                    # Debes reemplazar 'enable_pppoe_user' con el nombre real de tu función
                    result = contract.core_id.enable_pppoe_user(
                        username=contract.pppoe_user
                    )
                    if not result.get('success'):
                        raise UserError(_("Fallo al habilitar el usuario PPPoE en el Core: %s") % result.get('message'))

            except Exception as e:
                raise UserError(_("Ha ocurrido un error técnico al intentar reconectar el servicio: %s") % e)

            # Actualización de Estado
            contract.write({
                'state_service': 'active',
                'date_reconnection': fields.Date.context_today(self)
            })
        return True
    def action_ping_service(self):
        self.ensure_one()
        if not self.ip_address:
            raise UserError(_("No hay ninguna dirección IP asignada a este contrato para hacer ping."))

        ping_result = ""
        try:
            # --- Lógica de PING (Plantilla a adaptar) ---
            # Asumimos que un dispositivo central (como el Core) puede ejecutar el ping.
            # Debes reemplazar 'execute_ping' con tu función real.
            if self.core_id:
                ping_result = self.core_id.execute_ping(self.ip_address)
            else:
                ping_result = "No se ha configurado un router principal (Core) para ejecutar el ping desde allí."

        except Exception as e:
            ping_result = _("Fallo la ejecución del ping: %s") % e

        # --- Abrir el asistente con el resultado ---
        wizard = self.env['isp.ping.wizard'].create({'ping_output': ping_result})
        return {
            'name': _('Resultado de Ping'),
            'type': 'ir.actions.act_window',
            'res_model': 'isp.ping.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }
    def action_status_olt(self): pass
    def action_test_speed_service(self): pass
    def action_remove_service(self): pass
    def action_contract_reboot_onu(self): pass
    def action_change_ont_service(self): pass

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_isp_plan = fields.Boolean(string="Es un Plan ISP", help="Marcar si este producto es un plan de servicio para ISP.")