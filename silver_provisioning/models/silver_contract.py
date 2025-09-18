# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class IspContract(models.Model):
    _inherit = 'silver.contract'

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
    box_id = fields.Many2one('silver.box', string="Caja (CTO)")
    port_nap = fields.Char(string="Puerto en CTO")
    onu_id = fields.Many2one('silver.netdev', string="ONU/CPE")
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
    custom_channel_id = fields.Many2one('silver.wifi.channel.line', string="Canal WiFi")
    contract_mode_wan_ids = fields.One2many('silver.contract.wan.mode', 'contract_id', string="Configuración WAN")
    new_ip_address_id = fields.Many2one('silver.ip.pool.line', string="IP de Pool")
    consumption_ids = fields.One2many('silver.contract.consumption', 'contract_id', string="Registros de Consumo")
    radius_entry_ids = fields.One2many('silver.contract.radius.entry', 'contract_id', string="Entradas de RADIUS")

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
                    # Asumimos que tu modelo 'silver.olt' tiene un método para provisionar
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
                    # Asumimos que tu modelo 'silver.core' tiene un método para crear usuarios PPPoE
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
                    # Asumimos que tu modelo 'silver.olt' tiene un método para cortar el servicio
                    # Debes reemplazar 'cutoff_service_on_port' con el nombre real de tu función
                    result = contract.olt_id.cutoff_service_on_port(
                        port=contract.olt_port_id,
                        onu_serial=contract.serial_onu
                    )
                    if not result.get('success'):
                        raise UserError(_("Fallo al cortar el servicio en la OLT: %s") % result.get('message'))

                # --- EJEMPLO PARA PPPoE (Router Core) ---
                if contract.pppoe_user and contract.core_id:
                    # Asumimos que tu modelo 'silver.core' tiene un método para deshabilitar usuarios PPPoE
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
        wizard = self.env['silver.ping.wizard'].create({'ping_output': ping_result})
        return {
            'name': _('Resultado de Ping'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.ping.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def action_status_olt(self): pass
    def action_test_speed_service(self): pass
    def action_remove_service(self): pass
    def action_contract_reboot_onu(self): pass
    def action_change_ont_service(self): pass
