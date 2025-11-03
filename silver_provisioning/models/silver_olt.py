# -*- coding: utf-8 -*-
import re
import logging
from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.addons.base.models.ir_qweb_fields import Markup, escape, nl2br

import html

_logger = logging.getLogger(__name__)

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

    # --- Campo para Configuración WAN Avanzada ---
    vlan_priority = fields.Integer(string="Prioridad VLAN (PCP)", default=0,
                                   help="Valor de prioridad 802.1p (PCP/CoS) para QoS. Rango de 0 a 7.")

    contract_ids = fields.One2many('silver.contract', 'olt_id', string='Contratos')

    discovered_onu_ids = fields.One2many(
        'silver.olt.discovered.onu', 
        'olt_id', 
        string='ONUs Descubiertas'
    )

    def action_discover_onus(self):
        self.ensure_one()
        netdev = self.netdev_id
        if not netdev:
            raise UserError(_("La OLT no tiene un dispositivo de red configurado."))

       # command = "show onu auto-find detail-info"

        base_commands = [
            f"configure terminal",
            f"interface gpon 0/1",
            f"show onu auto-find detail-info",
            "exit", "exit"
        ]


        output_log = ""
        try:
            with netdev._get_olt_connection() as conn:


                onu_created_on_olt = False
                for command in base_commands:
                    success, clean_response, full_output = conn.execute_command(command)
                    output_log += f"\n{full_output}"
                    if f"show onu" in command:
                        break
                        #onu_created_on_olt = True
                    print(("ooutputt", 'a', output_log, success, clean_response))

                    if not success:
                        raise UserError(_("Error al ejecutar el comando en la OLT: %s") % full_output)
        except Exception as e:
            raise UserError(_("Fallo la conexión con la OLT: %s") % e)

        # --- Lógica de Procesamiento de Salida ---
        lines = full_output.strip().splitlines()
        header_line = None
        onu_vals_list = []
        
        for i, line in enumerate(lines):
            if 'OltIndex' in line and 'SN' in line:
                header_line = line
                data_lines = lines[i+1:]
                break
        
        if header_line:
            headers = ['OltIndex', 'SN', 'PW', 'LOID', 'Model', 'Ver', 'LOIDPW']
            positions = {h: header_line.find(h) for h in headers if header_line.find(h) != -1}
            sorted_headers = sorted(positions.keys(), key=lambda h: positions[h])
            slices = {h: (positions[h], positions[sorted_headers[i+1]] if i + 1 < len(sorted_headers) else len(header_line)) for i, h in enumerate(sorted_headers)}

            for line in data_lines:
                if not line.strip() or '------' in line: continue
                parts = {h: line[start:end].strip() for h, (start, end) in slices.items()}
                if parts.get('OltIndex') and parts.get('SN'):
                    onu_vals_list.append({
                        'olt_index': parts.get('OltIndex', ''), 'serial_number': parts.get('SN', ''),
                        'password': parts.get('PW', ''), 'loid': parts.get('LOID', ''),
                        'model_name': parts.get('Model', ''), 'version': parts.get('Ver', ''),
                        'loid_password': parts.get('LOIDPW', ''),
                    })

        # Realizar el "Upsert"
        # --- Lógica de Sincronización Mejorada ---
        DiscoveredOnu = self.env['silver.olt.discovered.onu']
        
        # 1. Obtener seriales de ONUs ya asignadas en esta OLT para no tocarlas
        assigned_onus = DiscoveredOnu.search([('olt_id', '=', self.id), ('is_assigned', '=', True)])
        assigned_serials = set(assigned_onus.mapped('serial_number'))

        # 2. Eliminar todas las ONUs NO asignadas de esta OLT
        unassigned_onus_to_delete = DiscoveredOnu.search([('olt_id', '=', self.id), ('is_assigned', '=', False)])
        if unassigned_onus_to_delete:
            unassigned_onus_to_delete.unlink()

        # 3. Crear solo las ONUs descubiertas que no estén ya asignadas
        onus_to_create = []
        for vals in onu_vals_list:
            if vals['serial_number'] not in assigned_serials:
                vals['olt_id'] = self.id
                onus_to_create.append(vals)
        
        if onus_to_create:
            DiscoveredOnu.create(onus_to_create)

        # --- Comportamiento Condicional del Retorno ---
        if self.env.context.get('called_from_contract'):
            # Si se llama desde el contrato, solo recargar la vista actual
            return {'type': 'ir.actions.client', 'tag': 'reload'}
        else:
            # Si se llama desde la OLT, abrir la ventana flotante
            return {
                'name': _('ONUs Descubiertas'),
                'type': 'ir.actions.act_window',
                'res_model': 'silver.olt.discovered.onu',
                'view_mode': 'tree,form',
                'domain': [('olt_id', '=', self.id)],
                'target': 'new',
            }

    def write(self, vals):
        # Campos monitoreados para la sincronización masiva
        monitored_fields = [
            'profile_dba_internet', 'tcont', 'gemport', 'service_port_internet',
            'primary_dns', 'secondary_dns', 'is_enable_remote_access_onu',
            'ont_lineprofile_value', 'ont_srvprofile_value', 'vlan_mgn_tr069'
        ]

        # Comprobar si alguno de los campos monitoreados ha cambiado
        if any(field in vals for field in monitored_fields):
            # Si hay cambios, marcamos el registro como que tiene cambios pendientes.
            # Usamos sudo() para escribir en un campo readonly.
            self.sudo().write({'pending_changes': True})

        # Llamamos al write original para que guarde todos los cambios.
        return super(SilverOlt, self).write(vals)

    def action_sync_olt_manual(self):
        self.ensure_one()

        # Obtener los valores actuales de los campos monitoreados
        current_values = self.read([
            'profile_dba_internet', 'tcont', 'gemport', 'service_port_internet',
            'primary_dns', 'secondary_dns', 'is_enable_remote_access_onu',
            'ont_lineprofile_value', 'ont_srvprofile_value', 'vlan_mgn_tr069'
        ])[0]
        
        # Filtrar los campos que no son nulos o falsos para aplicar
        changes_to_apply = {key: val for key, val in current_values.items() if val}

        if not changes_to_apply:
            raise UserError(_("No hay cambios pendientes o valores que aplicar."))

        affected_contracts = self.env['silver.contract'].search([
            ('olt_id', '=', self.id),
            ('state_service', '=', 'active'),
            ('link_type', '=', 'fiber')
        ])

        if not affected_contracts:
            self.env.user.notify_info(
                title=_("Sin Contratos Afectados"),
                message=_("No se encontraron contratos activos de fibra para aplicar los cambios.")
            )
            return

        # --- Construcción de la Lista de Comandos Optimizada ---
        commands = ["configure terminal"]
        
        for contract in affected_contracts.filtered(lambda c: c.olt_port_id and c.onu_pon_id):
            commands.append(f"interface gpon {contract.olt_port_id.name}")
            
            if 'profile_dba_internet' in changes_to_apply:
                tcont = self.tcont or '1'
                new_profile = changes_to_apply['profile_dba_internet']
                commands.append(f"onu {contract.onu_pon_id} tcont {tcont} dba {new_profile}")

            if 'ont_lineprofile_value' in changes_to_apply:
                commands.append(f"onu {contract.onu_pon_id} line-profile {changes_to_apply['ont_lineprofile_value']}")

            if 'ont_srvprofile_value' in changes_to_apply:
                commands.append(f"onu {contract.onu_pon_id} service-profile {changes_to_apply['ont_srvprofile_value']}")

            if 'is_enable_remote_access_onu' in changes_to_apply:
                action = "permit" if changes_to_apply['is_enable_remote_access_onu'] else "deny"
                commands.append(f"ont {contract.onu_pon_id} wan remote-access {action}")

            if 'primary_dns' in changes_to_apply or 'secondary_dns' in changes_to_apply:
                primary_dns = changes_to_apply.get('primary_dns', self.primary_dns)
                secondary_dns = changes_to_apply.get('secondary_dns', self.secondary_dns)
                if primary_dns:
                     commands.append(f"ont {contract.onu_pon_id} wan dns primary {primary_dns}")
                if secondary_dns:
                     commands.append(f"ont {contract.onu_pon_id} wan dns secondary {secondary_dns}")

            commands.append("exit")

        commands.extend(["exit"])
        if self.is_write_olt:
            commands.append("write")

        # --- Ejecución en una Sola Sesión ---
        netdev = self.netdev_id
        if not netdev:
            raise UserError(_("La OLT no tiene un dispositivo de red configurado."))

        log_messages = []
        try:
            with netdev._get_olt_connection() as conn:
                for command in commands:
                    success, response, output = conn.execute_command(command)
                    if not success:
                        log_messages.append(_("Error en comando '%s': %s") % (command, output))
        
        except Exception as e:
            raise UserError(_("Fallo la conexión con la OLT: %s") % e)

        # --- Notificación al Usuario y reseteo de la bandera ---
        if log_messages:
            error_summary = "\n".join(log_messages)
            self.env.user.notify_warning(
                title=_("Sincronización con Errores"),
                message=_("Ocurrieron errores al aplicar los cambios en %s ONUs:\n%s") % (len(affected_contracts), error_summary),
                sticky=True
            )
        else:
            self.env.user.notify_success(
                title=_("Éxito"),
                message=_("Los cambios se aplicaron correctamente a %s ONUs.") % len(affected_contracts)
            )
            # Si todo fue exitoso, reseteamos la bandera de cambios pendientes.
            self.sudo().write({'pending_changes': False})

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
            success, clean_response, full_output = conn.execute_command(command)
            output_log += f"\n{full_output}"
            if not success:
                raise UserError(f"Error ejecutando comando base '{command}':\n{clean_response}")
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
                success, clean_response, full_output = conn.execute_command(command)
                output_log += f"\n{full_output}"
                if not success:
                    use_simple_wifi_fallback = True
                    output_log += f"\n--- Comando WiFi avanzado falló ({clean_response}), intentando fallback a simple ---\\n"
            except Exception as e:
                use_simple_wifi_fallback = True
                output_log += f"\n--- Excepción en comando WiFi avanzado ({e}), intentando fallback a simple ---\\n"

            if not use_simple_wifi_fallback:
                for line in contract.wifi_line_ids[1:]:
                    hide_cmd = "enable" if line.is_hidden else "disable"
                    command = f"onu {onu_id} pri wifi_ssid {line.ssid_index} name {line.name} hide {hide_cmd} auth_mode {line.auth_mode} encrypt_type {line.encrypt_type} shared_key {line.password} rekey_interval 0"
                    success, clean_response, full_output = conn.execute_command(command)
                    output_log += f"\n{full_output}"
                    if not success:
                        raise UserError(f"Error en config. WiFi avanzada '{command}':\n{clean_response}")
            else:
                first_line = contract.wifi_line_ids[0]
                simple_commands = [
                    f"onu {onu_id} wifi ssid {first_line.name}",
                    f"onu {onu_id} wifi key {first_line.password}"
                ]
                for command in simple_commands:
                    success, clean_response, full_output = conn.execute_command(command)
                    output_log += f"\n{full_output}"
                    if not success:
                        raise UserError(f"Error en config. WiFi simple (fallback) '{command}':\n{clean_response}")
        return output_log

    def _provision_onu_wan(self, contract, conn, output_log, vlan_id):
        """Provisiona la configuración WAN avanzada en la ONU. Asume que ya se está en el modo de configuración de la interfaz GPON."""
        onu_id = contract.onu_pon_id
        if self.is_gestion_pppoe and not contract.is_bridge:
            cmd_get_index = f"onu {onu_id} pri wan_adv add route"
            success, clean_response, full_output = conn.execute_command(cmd_get_index)
            output_log += f"\n{full_output}"
            if not success:
                raise UserError(f"Error al iniciar config. WAN avanzada:\n{clean_response}")
            
            match = re.search(r"number is (\d+)", clean_response) # Buscar en la respuesta limpia
            if not match:
                raise UserError(f"No se pudo extraer el wan_index de la respuesta de la OLT:\n{clean_response}")
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
                success, clean_response, full_output = conn.execute_command(command)
                output_log += f"\n{full_output}"
                if not success:
                    raise UserError(f"Error en config. WAN avanzada '{command}':\n{clean_response}")
        return output_log

    def _execute_with_logging(self, contract, steps_or_commands, subject):
        """
        Método centralizado que gestiona la conexión, ejecución de comandos y logging robusto al chatter.
        Acepta una lista de pasos ('base', 'wifi', 'wan') o una lista de comandos directos.
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

        #if 1:
        try:
            conn = netdev._get_olt_connection()
            success, message = conn.connect()
            if not success:
                raise ConnectionError(message)

            # --- Secuencia de Comandos ---
            pon_port_val = f"{contract.olt_card_id.num_card or contract.olt_port_id.olt_card_id.num_card}/{contract.olt_port_id.num_port}"
            initial_commands = ["configure terminal", f"interface gpon {pon_port_val}"]
            for command in initial_commands:
                success, response, output = conn.execute_command(command)
                output_log += f"$ {command}\n{output}\n"
                if not success:
                    raise UserError(f"Error en comando inicial '{command}':\n{output}")

            # --- Pasos de Aprovisionamiento o Comandos Directos ---
            if isinstance(steps_or_commands, list) and all(isinstance(i, str) for i in steps_or_commands):
                # Si es una lista de strings, verificamos si son pasos o comandos
                if steps_or_commands[0] in ['base', 'wifi', 'wan']:
                    # (El código de manejo de 'base', 'wifi', 'wan' también debe ser actualizado
                    # para manejar la nueva tupla de retorno si llaman a execute_command directamente,
                    # pero por ahora nos centramos en el flujo principal)
                    steps = steps_or_commands
                    vlan_id = contract.vlan_id or self.vlan_id
                    if 'base' in steps:
                        log, onu_created, p_port, v_id = self._provision_onu_base(contract, conn, "")
                        output_log += log
                        onu_created_on_olt = onu_created
                        pon_port = p_port
                        vlan_id = v_id
                        base_config_successful = True
                    if 'wifi' in steps:
                        output_log += self._provision_onu_wifi(contract, conn, "")
                    if 'wan' in steps:
                        if not vlan_id:
                            raise UserError("No se pudo determinar la VLAN para la configuración WAN.")
                        output_log += self._provision_onu_wan(contract, conn, "", vlan_id)
                else: # Es una lista de comandos directos
                    for command in steps_or_commands:
                        success, clean_response, full_output = conn.execute_command(command)
                        output_log += f"\n{full_output}"
                        if not success:
                            raise UserError(f"Error ejecutando comando '{command}':\n{clean_response}")

            # --- Comandos Finales ---
            final_commands = ["exit", "exit", "write"]
            for command in final_commands:
                success, clean_response, full_output = conn.execute_command(command)
                output_log += f"\n{full_output}"
                if not success:
                    output_log += f"\nADVERTENCIA: El comando final '{command}' falló con el mensaje: {clean_response}\n"

            return True

        #else:
        except Exception as e:
            output_log += f"\n--- ERROR DETECTADO ---\n{e}\n"
            if onu_created_on_olt and not base_config_successful and pon_port and conn:
                output_log += "\n--- INICIANDO ROLLBACK EN OLT ---\\n"
                rollback_commands = [
                    "configure terminal", f"interface gpon {pon_port}",
                    f"no onu {contract.onu_pon_id}",
                    "exit", "exit", "write"
                ]
                for cmd in rollback_commands:
                    _success, _clean_response, _full_output = conn.execute_command(cmd)
                    output_log += f"\n{_full_output}"
            # Re-lanzar la excepción para que Odoo la muestre al usuario
            raise UserError(f"Fallo en la operación OLT:\n{e}\n\nConsulte el historial del contrato para ver el log completo.\n{output_log}") from None
        
        finally:
            if conn:
                conn.disconnect()
            # Publicar en el chatter SIEMPRE, al final de todo, en una transacción separada.
            if output_log:
                try:
                    with self.env.registry.cursor() as new_cr:
                        # Crear un nuevo entorno con el nuevo cursor
                        new_env = self.env(cr=new_cr)
                        # Obtener el contrato en este nuevo entorno para evitar problemas de caché/transacción
                        contract_in_new_env = new_env['silver.contract'].browse(contract.id)
                        # Publicar el mensaje.
                        o = html.escape(output_log).replace("\n", '<br/>')
                        contract_in_new_env.message_post(body=f"{Markup('<strong>')}{o}{Markup('</strong>')}", subject=subject,
                                                         body_is_html=True,
                                                         #message_type='comment',
                                                          subtype_xmlid='mail.mt_comment')
                        # Forzar el commit en el nuevo cursor para que el log persista incluso si la transaccion principal falla.
                        new_cr.commit()
                except Exception as log_e:
                    # Si el logging falla, no debemos ocultar el error original.
                    # Simplemente lo registramos en el log del servidor.
                    _logger.error(f"Fallo al intentar escribir el log de aprovisionamiento en el chatter del contrato {contract.name}: {log_e}")

    def action_provision_onu(self, contract):
        """Orquesta el aprovisionamiento completo de una nueva ONU."""
        return self._execute_with_logging(contract, ['base', 'wifi', 'wan'], "Registro de Aprovisionamiento OLT (Completo)")

    def provision_onu_base(self, contract):
        """Acción pública para ejecutar solo el aprovisionamiento base."""
        return self._execute_with_logging(contract, ['base'], "Registro de Aprovisionamiento OLT (Base)")

    def provision_onu_wifi(self, contract):
        """Acción pública para ejecutar solo la configuración WiFi."""
        return self._execute_with_logging(contract, ['wifi'], "Registro de Aprovisionamiento OLT (WiFi)")

    def provision_onu_wan(self, contract):
        """Acción pública para ejecutar solo la configuración WAN."""
        return self._execute_with_logging(contract, ['wan'], "Registro de Aprovisionamiento OLT (WAN)")

    def disable_onu(self, contract):
        """Desactiva el puerto de la ONU (Corte de servicio)."""
        commands = [ #f"interface gpon {pon_port}",
                     f"onu {contract.onu_pon_id} deactivate"]
        return self._execute_with_logging(contract, commands, "Registro de Corte de Servicio OLT")

    def enable_onu(self, contract):
        """Reactiva el puerto de la ONU (Reconexión de servicio)."""
        commands = [ #f"interface gpon {pon_port}",
                     f"onu {contract.onu_pon_id} activate"]
        return self._execute_with_logging(contract, commands, "Registro de Reconexión de Servicio OLT")

    def reboot_onu(self, contract):
        """Reinicia la ONU."""
        commands = [f"onu {contract.onu_pon_id} reboot"]
        return self._execute_with_logging(contract, commands, "Registro de Reinicio de ONU")

    def action_view_contracts(self):
        return self.access_point_id.action_view_contracts()
