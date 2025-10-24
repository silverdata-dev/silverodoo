# -*- coding: utf-8 -*-
import re
from odoo import models, fields
from odoo.exceptions import UserError

class SilverOlt(models.Model):
    _inherit = 'silver.olt'
    _inherits = {'silver.access_point': 'access_point_id'}

    access_point_id = fields.Many2one(
        'silver.access_point', 
        string='Registro de Provisioning', 
        required=True, 
        ondelete='cascade',
        help="Registro de provisioning asociado a esta OLT."
    )
    pending_changes_json = fields.Text(string="Cambios Pendientes (JSON)", readonly=True, copy=False)

    # --- Campo para Configuración WAN Avanzada ---
    vlan_priority = fields.Integer(string="Prioridad VLAN (PCP)", default=0,
                                   help="Valor de prioridad 802.1p (PCP/CoS) para QoS. Rango de 0 a 7.")

    def write(self, vals):
        # Campos monitoreados para la sincronización masiva
        monitored_fields = ['profile_dba_internet', 'tcont', 'gemport', 'service_port_internet']
        
        detected_changes = {}
        for field in monitored_fields:
            if field in vals:
                detected_changes[field] = vals[field]
        
        if detected_changes:
            # Guardamos los cambios detectados en formato JSON para usarlos en el wizard
            # Usamos el ORM para evitar recursión infinita en este write.
            super(SilverOlt, self).write({'pending_changes_json': str(detected_changes)})

        return super(SilverOlt, self).write(vals)

    def action_open_sync_wizard(self):
        self.ensure_one()
        
        changes = eval(self.pending_changes_json or '{}')
        if not changes:
            raise UserError(_("No hay cambios pendientes para sincronizar."))

        affected_contracts = self.env['silver.contract'].search([
            ('olt_id', '=', self.id),
            ('state_service', '=', 'active'),
            ('link_type', '=', 'fiber')
        ])

        ctx = {
            'default_olt_id': self.id,
            'default_contract_ids': [(6, 0, affected_contracts.ids)],
            'default_new_profile_dba': changes.get('profile_dba_internet'),
            'default_new_tcont': changes.get('tcont'),
            'default_new_gemport': changes.get('gemport'),
            'default_new_service_port': changes.get('service_port_internet'),
        }

        return {
            'name': _('Asistente de Sincronización de ONUs'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.olt.sync.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }

    def _provision_onu_base(self, contract, conn, output_log):
        """Ejecuta los comandos base de aprovisionamiento de la ONU. Asume que ya se está en el modo de configuración de la interfaz GPON."""
        # --- Recopilación y Validación de Parámetros ---
        pon_port = f"{contract.olt_card_id.num_card or contract.olt_port_id.olt_card_id.num_card}/{contract.olt_port_id.num_port}"
        onu_id = contract.onu_pon_id
        serial_number = contract.serial_number
        profile_name = contract.model_name
        tcont = self.tcont
        dba_profile = self.profile_dba_internet
        gemport = self.gemport
        vlan_id = contract.vlan_id or self.vlan_id
        service_port = self.service_port_internet
        service_name = contract.service_type_id.name
        description = f"{contract.name}-{contract.partner_id.vat}-{contract.partner_id.name}".replace(" ", "_")

        required_params = {
            "Puerto PON": pon_port, "ID de ONU en PON": onu_id, "Serial ONU": serial_number,
            "Modelo de ONU (Profile)": profile_name, "Tcont": tcont, "DBA Profile": dba_profile,
            "Gemport": gemport, "VLAN": vlan_id, "Service Port": service_port
        }
        missing_params = [key for key, value in required_params.items() if not value]
        if missing_params:
            raise UserError(f"Faltan parámetros requeridos: {', '.join(missing_params)}")

        base_commands = [
            f"onu add {onu_id} profile {profile_name} sn {serial_number}",
            f"onu {onu_id} tcont {tcont} dba {dba_profile}",
            f"onu {onu_id} gemport {gemport} tcont {tcont}",
            f"onu {onu_id} service {service_name or 'Internet'} gemport {gemport} vlan {vlan_id}",
            f"onu {onu_id} service-port {service_port} gemport {gemport} uservlan {vlan_id} vlan {vlan_id}",
            f"onu {onu_id} portvlan veip 1 mode tag vlan {vlan_id}",
            f"onu {onu_id} desc {description}",
        ]

        onu_created_on_olt = False
        for command in base_commands:
            success, output = conn.execute_command(command)
            output_log += f"$ {command}\n{output}\n"
            if not success:
                raise UserError(f"Error ejecutando comando base '{command}':\n{output}")
            if f"onu add {onu_id}" in command:
                onu_created_on_olt = True
        
        return output_log, onu_created_on_olt, pon_port, vlan_id

    def _provision_onu_wifi(self, contract, conn, output_log):
        """Provisiona la configuración WiFi en la ONU. Asume que ya se está en el modo de configuración de la interfaz GPON."""
        onu_id = contract.onu_pon_id
        if not contract.is_bridge and contract.wifi_line_ids:
            use_simple_wifi_fallback = False
            # Intentamos ejecutar el comando avanzado con la primera línea de WiFi
            try:
                first_line = contract.wifi_line_ids[0]
                hide_cmd = "enable" if first_line.is_hidden else "disable"
                command = f"onu {onu_id} pri wifi_ssid {first_line.ssid_index} name {first_line.name} hide {hide_cmd} auth_mode {first_line.auth_mode} encrypt_type {first_line.encrypt_type} shared_key {first_line.password} rekey_interval 0"
                success, output = conn.execute_command(command)
                output_log += f"$ {command}\n{output}\n"
                if not success:
                    use_simple_wifi_fallback = True
                    output_log += "--- Comando WiFi avanzado falló, intentando fallback a simple ---\n"
            except Exception as e:
                use_simple_wifi_fallback = True
                output_log += f"--- Excepción en comando WiFi avanzado ({e}), intentando fallback a simple ---\n"

            if not use_simple_wifi_fallback:
                for line in contract.wifi_line_ids[1:]:
                    hide_cmd = "enable" if line.is_hidden else "disable"
                    command = f"onu {onu_id} pri wifi_ssid {line.ssid_index} name {line.name} hide {hide_cmd} auth_mode {line.auth_mode} encrypt_type {line.encrypt_type} shared_key {line.password} rekey_interval 0"
                    success, output = conn.execute_command(command)
                    output_log += f"$ {command}\n{output}\n"
                    if not success:
                        raise UserError(f"Error en config. WiFi avanzada '{command}':\n{output}")
            else:
                first_line = contract.wifi_line_ids[0]
                simple_commands = [
                    f"onu {onu_id} wifi ssid {first_line.name}",
                    f"onu {onu_id} wifi key {first_line.password}"
                ]
                for command in simple_commands:
                    success, output = conn.execute_command(command)
                    output_log += f"$ {command}\n{output}\n"
                    if not success:
                        raise UserError(f"Error en config. WiFi simple (fallback) '{command}':\n{output}")
        return output_log

    def _provision_onu_wan(self, contract, conn, output_log, vlan_id):
        """Provisiona la configuración WAN avanzada en la ONU. Asume que ya se está en el modo de configuración de la interfaz GPON."""
        onu_id = contract.onu_pon_id
        if self.is_gestion_pppoe and not contract.is_bridge:
            cmd_get_index = f"onu {onu_id} pri wan_adv add route"
            success, output = conn.execute_command(cmd_get_index)
            output_log += f"$ {cmd_get_index}\n{output}\n"
            if not success:
                raise UserError(f"Error al iniciar config. WAN avanzada:\n{output}")
            
            match = re.search(r"number is (\d+)", output)
            if not match:
                raise UserError(f"No se pudo extraer el wan_index de la respuesta de la OLT:\n{output}")
            wan_index = match.group(1)

            admin_control_cmd = "enable" if self.is_control_admin else "disable"
            user_control_cmd = "disable" if self.is_control_admin else "enable"
            
            advanced_wan_commands = [
                f"onu {onu_id} pri wan_adv index {wan_index} route mode internet mtu {self.mtu}",
                f"onu {onu_id} pri wan_adv index {wan_index} route both pppoe proxy disable user {contract.pppoe_user} pwd {contract.pppoe_password} mode auto nat enable",
                f"onu {onu_id} pri wan_adv index {wan_index} route both client_address enable client_prifix enable",
                f"onu {onu_id} pri wan_adv index {wan_index} vlan tag wan_vlan {vlan_id} {self.vlan_priority}",
                f"onu {onu_id} pri wan_adv commit",
                f"onu {onu_id} pri username admin_control {admin_control_cmd} admin {self.admin_user} user_control {user_control_cmd}",
            ]
            for command in advanced_wan_commands:
                success, output = conn.execute_command(command)
                output_log += f"$ {command}\n{output}\n"
                if not success:
                    raise UserError(f"Error en config. WAN avanzada '{command}':\n{output}")
        return output_log

    def action_provision_onu(self, contract):
        """
        Orquesta el aprovisionamiento completo de una nueva ONU.
        Gestiona una única conexión para ejecutar todos los pasos en secuencia.
        """
        self.ensure_one()
        netdev = self.netdev_id
        if not netdev:
            raise UserError("No hay dispositivo de red configurado para esta OLT.")

        output_log = ""
        conn = None
        onu_created_on_olt = False
        base_config_successful = False
        pon_port = None
        
        try:
            conn = netdev._get_olt_connection()
            success, message = conn.connect()
            if not success:
                raise ConnectionError(message)

            # --- Secuencia de Comandos ---
            pon_port_val = f"{contract.olt_card_id.num_card or contract.olt_port_id.olt_card_id.num_card}/{contract.olt_port_id.num_port}"
            initial_commands = ["configure terminal", f"interface gpon {pon_port_val}"]
            for command in initial_commands:
                success, output = conn.execute_command(command)
                output_log += f"$ {command}\n{output}\n"
                if not success:
                    raise UserError(f"Error en comando inicial '{command}':\n{output}")

            # --- Pasos de Aprovisionamiento ---
            output_log, onu_created_on_olt, pon_port, vlan_id = self._provision_onu_base(contract, conn, output_log)
            base_config_successful = True
            
            output_log = self._provision_onu_wifi(contract, conn, output_log)
            output_log = self._provision_onu_wan(contract, conn, output_log, vlan_id)

            # --- Comandos Finales ---
            final_commands = ["exit", "exit", "write"]
            for command in final_commands:
                success, output = conn.execute_command(command)
                output_log += f"$ {command}\n{output}\n"
                if not success:
                    # No lanzamos error aquí para asegurar que la desconexión ocurra.
                    # El fallo en 'write' es problemático pero no debe impedir el cierre.
                    output_log += f"ADVERTENCIA: El comando final '{command}' falló.\n"

            return True

        except (ConnectionError, UserError) as e:
            if onu_created_on_olt and not base_config_successful and pon_port:
                output_log += "\n--- ERROR DETECTADO, INICIANDO ROLLBACK EN OLT ---\n"
                # El rollback necesita su propia secuencia de comandos dentro de la conexión existente
                rollback_commands = [
                    "configure terminal",
                    f"interface gpon {pon_port}",
                    f"no onu {contract.onu_pon_id}",
                    "exit", "exit", "write"
                ]
                for cmd in rollback_commands:
                    _success, _output = conn.execute_command(cmd)
                    output_log += f"$ {cmd}\n{_output}\n"
            
            raise UserError(f"Fallo en el aprovisionamiento:\n{e}\n\nLog de Comandos:\n{output_log}") from None
        
        finally:
            if conn:
                conn.disconnect()

    def provision_onu_base(self, contract):
        """Acción pública para ejecutar solo el aprovisionamiento base."""
        self.ensure_one()
        netdev = self.netdev_id
        if not netdev:
            raise UserError("No hay dispositivo de red configurado para esta OLT.")
        
        output_log = ""
        conn = None
        try:
            conn = netdev._get_olt_connection()
            conn.connect()
            pon_port_val = f"{contract.olt_card_id.num_card or contract.olt_port_id.olt_card_id.num_card}/{contract.olt_port_id.num_port}"
            conn.execute_command("configure terminal")
            conn.execute_command(f"interface gpon {pon_port_val}")
            self._provision_onu_base(contract, conn, output_log)
            conn.execute_command("exit")
            conn.execute_command("exit")
            conn.execute_command("write")
        except Exception as e:
            raise UserError(f"Fallo en aprovisionamiento base: {e}")
        finally:
            if conn:
                conn.disconnect()
        return True

    def provision_onu_wifi(self, contract):
        """Acción pública para ejecutar solo la configuración WiFi."""
        self.ensure_one()
        netdev = self.netdev_id
        if not netdev:
            raise UserError("No hay dispositivo de red configurado para esta OLT.")
        
        output_log = ""
        conn = None
        try:
            conn = netdev._get_olt_connection()
            conn.connect()
            pon_port_val = f"{contract.olt_card_id.num_card or contract.olt_port_id.olt_card_id.num_card}/{contract.olt_port_id.num_port}"
            conn.execute_command("configure terminal")
            conn.execute_command(f"interface gpon {pon_port_val}")
            self._provision_onu_wifi(contract, conn, output_log)
            conn.execute_command("exit")
            conn.execute_command("exit")
            conn.execute_command("write")
        except Exception as e:
            raise UserError(f"Fallo en configuración WiFi: {e}")
        finally:
            if conn:
                conn.disconnect()
        return True

    def provision_onu_wan(self, contract):
        """Acción pública para ejecutar solo la configuración WAN."""
        self.ensure_one()
        netdev = self.netdev_id
        if not netdev:
            raise UserError("No hay dispositivo de red configurado para esta OLT.")
        
        output_log = ""
        conn = None
        try:
            conn = netdev._get_olt_connection()
            conn.connect()
            pon_port_val = f"{contract.olt_card_id.num_card or contract.olt_port_id.olt_card_id.num_card}/{contract.olt_port_id.num_port}"
            vlan_id = contract.vlan_id or self.vlan_id
            if not vlan_id:
                raise UserError("No se pudo determinar la VLAN para la configuración WAN.")
            conn.execute_command("configure terminal")
            conn.execute_command(f"interface gpon {pon_port_val}")
            self._provision_onu_wan(contract, conn, output_log, vlan_id)
            conn.execute_command("exit")
            conn.execute_command("exit")
            conn.execute_command("write")
        except Exception as e:
            raise UserError(f"Fallo en configuración WAN: {e}")
        finally:
            if conn:
                conn.disconnect()
        return True

    def action_view_contracts(self):
        return self.access_point_id.action_view_contracts()