# -*- coding: utf-8 -*-
import re
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.base.models.ir_qweb_fields import Markup, escape, nl2br

import html
from datetime import datetime, timedelta

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
    last_discovered_date = fields.Datetime("Last Discovered Date")

    old_discovered = fields.Boolean(
        string="Old discovered",
        compute='_compute_old_discovered',
        store=False,  # No es necesario almacenarlo
    )

    def action_discover_onus(self):
        self.ensure_one()


       # command = "show onu auto-find detail-info"

        base_commands = [
            f"configure terminal",
            f"interface gpon 0/1",
            f"show onu auto-find detail-info",
            "exit", "exit"
        ]


        output_log = ""
        last_command_output = ""
        try:
            with self._get_olt_connection() as conn:
                onu_created_on_olt = False
                for command in base_commands:
                    success, clean_response, cmd_output = conn.execute_command(command)
                    output_log += f"\n{cmd_output}"
                    
                    if not success:
                        raise UserError(_("Error al ejecutar el comando en la OLT: %s") % cmd_output)

                    if "show onu" in command:
                        last_command_output = cmd_output
                        break
        except Exception as e:
            raise UserError(_("Fallo la conexión con la OLT: %s") % e)

        # --- Lógica de Procesamiento de Salida ---
        full_output = last_command_output
        lines = full_output.strip().splitlines()
        header_line = None
        onu_vals_list = []
        
        for i, line in enumerate(lines):
            if 'OltIndex' in line and 'SN' in line:
                header_line = line
                data_lines = lines[i+1:]
                break

        DiscoveredOnu = self.env['silver.olt.discovered.onu']

        if header_line:
            headers = ['OltIndex', 'SN', 'PW', 'LOID', 'Model', 'Ver', 'LOIDPW']
            positions = {h: header_line.find(h) for h in headers if header_line.find(h) != -1}
            sorted_headers = sorted(positions.keys(), key=lambda h: positions[h])
            slices = {h: (positions[h], positions[sorted_headers[i+1]] if i + 1 < len(sorted_headers) else len(header_line)) for i, h in enumerate(sorted_headers)}

            for line in data_lines:
                if not line.strip() or '------' in line: continue
                parts = {h: line[start:end].strip() for h, (start, end) in slices.items()}
                if parts.get('OltIndex') and parts.get('SN'):
                    Product = self.env['product.product'];

                  #  Model = self.env['silver.hardware.model'];
                    modelname = parts.get('Model', '')
                    product = Product.search([('name', '=', modelname)], limit=1)
                    #model = Model.search([('name', '=', modelname)], limit=1)
                    #if (not model) or (not len(model)):
                    if (not product) or (not len(product)):
                        marcas = self.env['product.brand'].search([])
                        marca_id = None
                        for a in marcas:
                            if a.name and a.name in modelname:
                                marca_id = a
                                break
                        
                       # model = Model.create({'name': modelname, 'etype':'onu', 'brand_id': marca_id.id if marca_id else False})
                        product = Product.create(
                            {'name': modelname, 'etype': 'onu', 'brand_id': marca_id.id if marca_id else False})

                    onu_vals_list.append({
                        'olt_index': parts.get('OltIndex', ''), 'serial_number': parts.get('SN', ''),
                        'password': parts.get('PW', ''), 'loid': parts.get('LOID', ''),
                        'product_id': product.id,
                        #'hardware_model_id': model.id,
                       # 'model_name': parts.get('Model', ''),
                        'version': parts.get('Ver', ''),
                        'loid_password': parts.get('LOIDPW', ''),
                    })


            # Realizar el "Upsert"
            # --- Lógica de Sincronización Mejorada ---

        # 1. Obtener seriales de ONUs ya asignadas en esta OLT para no tocarlas
        #assigned_onus = DiscoveredOnu.search([('olt_id', '=', self.id), ('is_assigned', '=', True)])

        assigned_onus = DiscoveredOnu.search([('olt_id', '=', self.id), ('contract_id', '!=', False)])
        assigned_indexes = set(assigned_onus.mapped('olt_index'))

        # 2. Eliminar todas las ONUs NO asignadas de esta OLT
        unassigned_onus_to_delete = DiscoveredOnu.search([('olt_id', '=', self.id), ('contract_id', '=', False)])

        if unassigned_onus_to_delete:
            unassigned_onus_to_delete.unlink()

        # 3. Crear solo las ONUs descubiertas que no estén ya asignadas
        onus_to_create = []
        for vals in onu_vals_list:
            if vals['olt_index'] not in assigned_indexes:
                vals['olt_id'] = self.id
                onus_to_create.append(vals)

        self.last_discovered_date = datetime.now()
        print(("last_discovered_date", self.last_discovered_date))

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
            ('linktype.has_olt', '!=', False)
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

        log_messages = []
        try:
            with self._get_olt_connection() as conn:
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

    def check_and_create_onu_profile(self, conn, profile, output_log):
        """
        Verifica si un perfil de ONU existe en la OLT y lo crea si no.
        """
        # Si estamos en modo de configuración de interfaz, debemos salir para gestionar perfiles.
        print(("preprofile", conn.prompt))
        if conn.prompt and 'config-pon' in conn.prompt:
            _logger.info("Saliendo del modo 'config-gpon-if' para gestionar perfiles.")
            cmd_exit_interface = "exit"
            success, full_output, clean_response = conn.execute_command(cmd_exit_interface)
            output_log += f"$ {cmd_exit_interface}\n{full_output}\n"
            if not success:
                # Esto sería un problema, ya que no podemos asegurar el estado.
                raise UserError(f"Error al intentar salir del modo de interfaz: {clean_response}")

        conn.execute_command("configure terminal")

        command = "show profile onu"
        print(("a"))
        success, full_output, clean_response = conn.execute_command(command)
        print(("b"))
        output_log += f"\n$ {command}\n{full_output}\n"
        if not success:
            # No lanzamos un error, solo advertimos, ya que el aprovisionamiento podría continuar
            # si el perfil se asume que existe. El siguiente comando fallará de todos modos.
            print(("noprofile"))
            output_log += f"ADVERTENCIA: No se pudo ejecutar 'show profile onu': {clean_response}\n"
            return output_log



        # Parsear la salida para encontrar perfiles existentes
        # Usamos una expresión regular más robusta para manejar diferentes espaciados
        profiles = re.findall(r"^\s*Name\s*:\s*(\S+)", full_output, re.MULTILINE)

        print(("profile", profiles))

        if profile.name in profiles:
            output_log += f"INFO: El perfil '{profile.name}' ya existe en la OLT.\n"
            return output_log

        # Si el perfil no existe, encontrar el ID máximo para crear uno nuevo
        output_log += f"INFO: El perfil '{profile.name}' no fue encontrado. Intentando crearlo...\n"
        ids = [int(i) for i in re.findall(r"^\s*Id\s*:\s*(\d+)", full_output, re.MULTILINE)]
        new_profile_id = max(ids) + 1 if ids else 1

        commands = [

            'configure terminal',
            f"profile onu id {new_profile_id} name {profile.name}",
            #'profile onu profile-name {}'.format(profile.name),
            'description {}'.format(profile.description or profile.name),
            'tcont-num {} gemport-num {}'.format(profile.tcont_num, profile.gemport_num),
            'port-num eth {} pots {} iphost {} ipv6host {} veip {}'.format(
                profile.port_num_eth, profile.pots, profile.iphost, profile.ipv6host, profile.veip),
            # The service-ability command needs careful construction
            'service-ability {} {} {} {} {} {}'.format(
                'N:1', 'yes' if profile.service_ability_n_1 else 'no',
                '1:P', 'yes' if profile.service_ability_1_p else 'no',
                '1:M', 'yes' if profile.service_ability_1_m else 'no'
            ),
            'commit',
            'exit',
            'exit'
        ]
        try:

            with self._get_olt_connection() as conn:
                for command in commands:
                    success, response, output = conn.execute_command(command)
                    output_log += f"$ {command}\n{output}\n"
                    if not success:
                        # You might want to check for specific non-critical errors here
                        # For now, any failure stops the process.
                        raise UserError(f"Error executing command '{command}':\n{output}")
            return output_log
        except (ConnectionError, UserError) as e:
            raise UserError(f"Operation failed:\n{e}\n\nLog:\n{output_log}")
        except Exception as e:
            # Catching unexpected errors
            raise UserError(f"An unexpected error occurred: {e}\n\nLog:\n{output_log}")

        #success, clean_response, full_output = conn.execute_command(create_command)
        print(("profonu ", full_output))
       # output_log += f"$ {create_command}\n{full_output}\n"
        if not success:
            # Si la creación del perfil falla, es un error crítico.
            raise UserError(f"Error al crear el perfil de ONU '{profile.name}':\n{clean_response}")

        output_log += f"ÉXITO: Perfil '{profile.name}' creado con ID {new_profile_id}.\n"

        # Si la creación fue exitosa, el prompt cambiará. Hacemos commit y salimos.
        # El prompt se ve como: gpon-olt-4-Silverdata(profile-onu:32)#
        #if "(profile-onu:" in full_output:
        if "success" in full_output:
            output_log += "INFO: Saliendo del modo de configuración de perfil.\n"
            
            # 1. Commit
            cmd_commit = "commit"
            success, clean_response, full_output = conn.execute_command(cmd_commit)
            output_log += f"$ {cmd_commit}\n{full_output}\n"
            if not success:
                raise UserError(f"Error al ejecutar 'commit' después de crear el perfil:\n{clean_response}")

            # 2. Exit
            cmd_exit = "exit"
            success, clean_response, full_output = conn.execute_command(cmd_exit)
            output_log += f"$ {cmd_exit}\n{full_output}\n"
            if not success:
                raise UserError(f"Error al ejecutar 'exit' después de crear el perfil:\n{clean_response}")

        return output_log

    @api.depends('last_discovered_date')
    def _compute_old_discovered(self):
        hace_cinco_minutos = datetime.now() - timedelta(minutes=5)

        for record in self:
            print(("old_discovered", record.last_discovered_date, record.old_discovered, hace_cinco_minutos, record.last_discovered_date < hace_cinco_minutos))

            if record.last_discovered_date:
                # 2. La condición es: La fecha de la BD (UTC) es menor que el límite (UTC)
                #    Es decir, la fecha es MÁS ANTIGUA que hace 5 minutos.
                record.old_discovered = record.last_discovered_date < hace_cinco_minutos
            else:
                record.old_discovered = False

    def _provision_onu_base(self, contract, conn, output_log):
        """Ejecuta los comandos base de aprovisionamiento de la ONU. Asume que ya se está en el modo de configuración de la interfaz GPON."""
        # --- Recopilación y Validación de Parámetros ---
        pon_port = f"{contract.olt_card_id.num_card or contract.olt_port_id.olt_card_id.num_card}/{contract.olt_port_id.num_port}"
        onu_id = contract.onu_pon_id
        serial_number = contract.serial_number
        profile_name = contract.profile_id.name
        tcont = self.tcont
        dba_profile = self.profile_dba_internet
        gemport = self.gemport
        vlanid = contract.vlan_id.vlanid
        service_port = self.service_port_internet
        service_name = contract.service_type_id.name
        description = f"{contract.name}-{contract.partner_id.vat}-{contract.partner_id.name}".replace(" ", "_")


        required_params = {
            "Puerto PON": pon_port,  "Serial ONU": serial_number, #"ID de ONU en PON": onu_id,
            "Modelo de ONU (Profile)": profile_name, "Tcont": tcont, "DBA Profile": dba_profile,
            "Gemport": gemport, "VLAN": vlanid, "Service Port": service_port
        }
        missing_params = [key for key, value in required_params.items() if not value]
        if missing_params:
            raise UserError(f"Faltan parámetros requeridos: {', '.join(missing_params)}")

        success, clean_response, full_output = conn.execute_command("show onu info")
        (onu_id2, s) = self.get_free_onuid(full_output, serial_number, onu_id)
        print(("free onu ", onu_id, onu_id2, serial_number, full_output))
        if onu_id != onu_id2:
            onu_id = onu_id2
            contract.onu_pon_id = onu_id


       # return

        base_commands = []
        if not s:
            base_commands.extend([            f"onu add {onu_id} profile {profile_name} sn {serial_number}"  ])
        base_commands.extend([
            f"onu {onu_id} tcont {tcont} dba {dba_profile}",
            f"onu {onu_id} gemport {gemport} tcont {tcont}",
            f"onu {onu_id} service {service_name or 'Internet'} gemport {gemport} vlan {vlanid}",
            f"onu {onu_id} service-port {service_port} gemport {gemport} uservlan {vlanid} vlan {vlanid}",
            f"onu {onu_id} portvlan veip 1 mode tag vlan {vlanid}",
            f"onu {onu_id} desc {description}",
            f"onu {onu_id} pri wan_adv commit",
            f"exit", "exit", "exit"
        ])


        onu_created_on_olt = False
        retry = 0
        for retries in [0,1]:
            if retry != retries: break
            for command in base_commands:
                success, clean_response, full_output = conn.execute_command(command)
                output_log += f"\n{clean_response}"

                if not success:
                    if "wan_adv commit" in command:
                        continue
                    print(("not output", full_output))
                    """if "not found or it's not commited" in full_output:
                        output_log += self._check_and_create_onu_profile(conn, profile_name, output_log)
                        
                        # Re-entrar al modo de interfaz, ya que la creación de perfil nos saca de él.
                        _logger.info(f"Re-entrando a la interfaz 'gpon {pon_port}' después de crear el perfil.")
                        cmd_reenter = f"interface gpon {pon_port}"
                        s_re, fo_re, cr_re = conn.execute_command(cmd_reenter)
                        output_log += f"\n{fo_re}"
                        if not s_re:
                            raise UserError(f"Fallo al re-entrar a la interfaz {pon_port} despues de crear el perfil: {cr_re}")

                        retry = 1
                        break"""

                    raise UserError(f"Error ejecutando comando base '{command}':\n{clean_response}")
                if f"onu add {onu_id}" in command:
                    onu_created_on_olt = True

        return output_log, onu_created_on_olt, pon_port, vlanid

    def _provision_onu_wifi(self, contract, conn, output_log):
        def getwifiname(config_text):
            for line in config_text.splitlines():
                # 2. Identificar la línea que comienza con "Name"
                if line.strip().startswith("Name"):
                    # 3. Dividir la línea por el primer ':' (el separador campo-valor)
                    # y tomar el segundo elemento (el valor).
                    value = line.split(':', 1)[1]

                    # 4. Limpiar el valor de cualquier espacio en blanco restante.
                    # Esto convierte una cadena de solo espacios en "".
                    return value.strip()
            return None

        """Provisiona la configuración WiFi en la ONU. Asume que ya se está en el modo de configuración de la interfaz GPON."""
        onu_id = contract.onu_pon_id
        if not contract.is_bridge and contract.wifi_line_ids:
            use_simple_wifi_fallback = False
            # Intentamos ejecutar el comando avanzado con la primera línea de WiFi
            d=dict()
            for line in contract.wifi_line_ids:
                d[line.ssid_index] = line
            print(("lines", line))
            for a in range(1, 9):
                line = d.get(a)
                if not line:
                    command = f"show onu {contract.onu_pon_id} pri wifi_ssid {a}"

                    success, clean_response, full_output = conn.execute_command(command)
                    print(("showed wifi ", full_output, clean_response))
                    ssid_name = getwifiname(full_output)
                    if not ssid_name: continue

                    command = f"onu {onu_id} pri wifi_ssid {a} disable name {ssid_name}"
                else:
                    hide_cmd = "enable" if line.is_hidden else "disable"
                    command = f"onu {onu_id} pri wifi_ssid {a} name {line.name} hide {hide_cmd} auth_mode {line.auth_mode} encrypt_type {line.encrypt_type} shared_key {line.password} rekey_interval 0"
                success, clean_response, full_output = conn.execute_command(command)
                #print(("wifioutput", full_output))
                output_log += f"{clean_response}\n"

                if not success:
                    raise UserError(f"Error en config. WIFI '{command}':\n{clean_response}")
            success, clean_response, full_output = conn.execute_command(f"onu {onu_id} pri wan_conn commit")
            output_log += f"{clean_response}\n"



        return output_log

    def _provision_onu_wan(self, contract, conn, output_log, vlanid, pon_port):
        """Provisiona la configuración WAN avanzada en la ONU. Asume que ya se está en el modo de configuración de la interfaz GPON."""
        onu_id = contract.onu_pon_id


        required_params = {
            "Puerto PON": pon_port, "ID de ONU en PON": onu_id, "PPPoe User": contract.pppoe_user,
            "PPPoe Password": contract.pppoe_password, "MTU": self.mtu,
             "VLAN": vlanid,
        }
        if (self.is_control_admin) :
            required_params['Usuario Admin'] = self.admin_user
            required_params['Password Admin'] = self.admin_passwd


        missing_params = [key for key, value in required_params.items() if not value]
        if missing_params:
            raise UserError(f"Faltan parámetros requeridos: {', '.join(missing_params)}")

        if 1:
       # if self.is_gestion_pppoe and not contract.is_bridge:
            wan_index = None
            #"""
            # 1. Check if WAN already exists
            cmd_check_wan = f"onu {onu_id} pri wan_adv show"
            success, clean_response, full_output = conn.execute_command(cmd_check_wan)
            output_log += f"\n{full_output}"

            print(("onu show", success, output_log))


            
            if "wanNumber" in output_log:
                current_index = None
                current_mode = None
                current_type = None
                current_vlan = None
                
                for line in clean_response.splitlines():
                    line = line.strip()
                    if line.startswith("WAN Index"):
                        parts = line.split(":")
                        if len(parts) > 1:
                            current_index = parts[1].strip()
                            # Reset per block
                            current_mode = None
                            current_type = None
                            current_vlan = None
                    elif line.startswith("WAN Mode"):
                        parts = line.split(":")
                        if len(parts) > 1:
                            current_mode = parts[1].strip().lower()
                    elif line.startswith("Connect Type"):
                         parts = line.split(":")
                         if len(parts) > 1:
                            current_type = parts[1].strip().lower()
                    elif line.startswith("VLAN ID"):
                         parts = line.split(":")
                         if len(parts) > 1:
                            current_vlan = parts[1].strip()

                   # print(("ll", current_index,  current_mode , current_type , current_vlan, vlanid))
                    # Check match
                    if current_index and current_mode == 'internet' and current_type == 'route': # and current_vlan == str(vlanid):
                        wan_index = current_index
                        output_log += f"\nINFO: Found existing WAN index {wan_index} matching configuration. Reusing it."
                        break
            #"""
            for a in [0, 1]:
                if not wan_index:
                    cmd_get_index = f"onu {onu_id} pri wan_adv add route"
                    success, clean_response, full_output = conn.execute_command(cmd_get_index)
                    output_log += f"\n{full_output}"
                    #if not success:

                    if not "Msg:" in full_output:
                        raise UserError(f"Error al iniciar config. WAN avanzada:\n{clean_response}")

                    match = re.search(r"number is (\d+)", clean_response) # Buscar en la respuesta limpia
                    if not match:
                        raise UserError(f"No se pudo extraer el wan_index de la respuesta de la OLT:\n{clean_response}")
                    wan_index = match.group(1)

                admin_control_cmd = f"enable {self.admin_user} {self.admin_passwd}" if self.is_control_admin else "disable"
                user_control_cmd = "disable" #if self.is_control_admin else "enable"

                wifis = [f"ssid{c.ssid_index}" for c in contract.wifi_line_ids ]


                advanced_wan_commands = [
                 #   f"onu {onu_id} pri factory_reset",
                    f"onu {onu_id} pri wan_adv index {wan_index} route mode internet mtu {self.mtu}",
                    f"onu {onu_id} pri wan_adv index {wan_index} route both pppoe proxy disable user {contract.pppoe_user} pwd {contract.pppoe_password} mode auto nat enable slaac enable",
                    f"onu {onu_id} pri wan_adv index {wan_index} route both client_address disable client_prifix enable",
                    f"onu {onu_id} pri wan_adv index {wan_index} vlan tag wan_vlan {vlanid} {self.vlan_priority}",
                    f"onu {onu_id} pri wan_adv index {wan_index} bind lan1 {' '.join(wifis)}",
                    f"onu {onu_id} pri username admin_control {admin_control_cmd} user_control {user_control_cmd}",
                    f"onu {onu_id} pri wan_adv commit",
                    #f"onu {onu_id} pri wan_adv commit"

                ]



                print(("comands", advanced_wan_commands))
                for command in advanced_wan_commands:
                    success, clean_response, full_output = conn.execute_command(command)
                    output_log += f"{clean_response}\n"

                    if success or  "wan_adv commit" in command:
                        continue
                    if not a:
                        wan_index = None
                        break
                    raise UserError(f"Error en config. WAN avanzada '{command}':\n{clean_response}")
                if wan_index: break
                output_log += f"not wan {a}"
        return output_log

    def _execute_with_logging(self, contract, steps_or_commands, subject):
        """
        Método centralizado que gestiona la conexión, ejecución de comandos y logging robusto al chatter.
        Acepta una lista de pasos ('base', 'wifi', 'wan') o una lista de comandos directos.
        """
        self.ensure_one()

        output_log = ""
        conn = None
        onu_created_on_olt = False
        base_config_successful = False
        pon_port = None

        print(("e1", steps_or_commands))
        #if 1:
        try:
            conn = self._get_olt_connection()
            success, message = conn.connect()
            if not success:
                raise ConnectionError(message)

            # --- Secuencia de Comandos ---
            pon_port_val = f"{contract.olt_card_id.num_card or contract.olt_port_id.olt_card_id.num_card}/{contract.olt_port_id.num_port}"
            
            # 1. Entrar en modo de configuración
            cmd_config_term = "configure terminal"
            success, response, output = conn.execute_command(cmd_config_term)
            output_log += f"$ {cmd_config_term}\n{response}\n"
            if not success:
                raise UserError(f"Error en comando inicial '{cmd_config_term}':\n{output}")

            # 2. Paso 'prebase': Verificar y crear perfil de ONU si es necesario
            is_base_provisioning = (isinstance(steps_or_commands, list) and
                                    'base' in steps_or_commands and
                                    steps_or_commands and steps_or_commands[0] in ['base', 'wifi', 'wan'])

            #if is_base_provisioning:
            #    profile_name = contract.model_name
            #    if profile_name:
            #        output_log = self._check_and_create_onu_profile(conn, profile_name, output_log)
            #    else:
            #        output_log += "\nADVERTENCIA: No se pudo verificar/crear el perfil de la ONU porque el contrato no tiene un modelo (perfil) asignado.\n"

            # 3. Entrar en la interfaz GPON
            cmd_interface = f"interface gpon {pon_port_val}"
            success, response, output = conn.execute_command(cmd_interface)
            output_log += f"$ {cmd_interface}\n{response}\n"
            if not success:
                raise UserError(f"Error en comando inicial '{cmd_interface}':\n{output}")

            # --- Pasos de Aprovisionamiento o Comandos Directos ---
            if isinstance(steps_or_commands, list) and all(isinstance(i, str) for i in steps_or_commands):
                # Si es una lista de strings, verificamos si son pasos o comandos
                if steps_or_commands[0] in ['base', 'wifi', 'wan']:
                    # (El código de manejo de 'base', 'wifi', 'wan' también debe ser actualizado
                    # para manejar la nueva tupla de retorno si llaman a execute_command directamente,
                    # pero por ahora nos centramos en el flujo principal)
                    steps = steps_or_commands
                    vlanid = contract.vlan_id.vlanid
                    if 'base' in steps:
                        log, onu_created, p_port, v_id = self._provision_onu_base(contract, conn, "")
                        output_log += log
                        onu_created_on_olt = onu_created
                        pon_port = p_port
                        vlanid = v_id
                        base_config_successful = True
                    if 'wifi' in steps:
                        output_log += self._provision_onu_wifi(contract, conn, "")
                    if 'wan' in steps:
                        if not vlanid:
                            raise UserError("No se pudo determinar la VLAN para la configuración WAN.")

                        print(("towan", conn))
                        output_log += self._provision_onu_wan(contract, conn, "", vlanid, pon_port_val)
                else: # Es una lista de comandos directos
                    for command in steps_or_commands:
                        success, clean_response, full_output = conn.execute_command(command)
                        output_log += f"{clean_response}\n"
                        if not success:
                            raise UserError(f"Error ejecutando comando '{command}':\n{clean_response}")

            # --- Comandos Finales ---
            final_commands = ["exit", "exit", "write"]
            for command in final_commands:
                success, clean_response, full_output = conn.execute_command(command)
                output_log += f"{clean_response}\n"
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
                    output_log += f"{_clean_response}\n"
            # Re-lanzar la excepción para que Odoo la muestre al usuario
            raise UserError(f"Fallo en la operación OLT:\n{e}\n\n{output_log}") from None
        
        finally:
            print(("finaly", output_log))
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
                        print(("message", o))
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


    def reset_onu(self, contract):
        """Reinicia la ONU."""
        commands = [f"onu {contract.onu_pon_id} pri factory_reset"]
        return self._execute_with_logging(contract, commands, "Registro de Reinicio de ONU")

    def terminate_onu(self, contract, pon_port_name):
        """Termina la ONU."""

        try:
            with self._get_olt_connection() as conn:
                # 1. Entrar en modo configuración

                success, output_log, full_output = conn.execute_command("configure terminal")

                # 2. Entrar a la interfaz GPON
                # Asumimos que pon_port_name viene limpio, ej: "0/1"
                cmd_interface = f"interface gpon {pon_port_name}"
                success, clean_response, full_output = conn.execute_command(cmd_interface)
                output_log += f"\n{clean_response}\n"

                if not success:
                    raise UserError(f"Error al entrar a la interfaz {pon_port_name}:\n{full_output}")

                # 3. Obtener información de ONUs
                cmd_show = "show onu info"
                success, clean_response, full_output = conn.execute_command(cmd_show)
                output_log += f"{clean_response}\n"

                (onuid, s) = self.get_free_onuid(full_output, serial=contract.stock_lot_id.name,  onu_id=contract.onu_pon_id, )

                print(("free onu s", onuid, s, contract.onu_pon_id))

                if s:
                    success, clean_response, full_output = conn.execute_command(f"no onu {onuid}")
                    output_log += f"{clean_response}\n"

                # 4. Salir limpiamente (opcional pero recomendado)
                conn.execute_command("exit")
                conn.execute_command("exit")

                o = html.escape(output_log).replace("\n", '<br/>')

                contract.message_post(body=f"{Markup('<strong>')}{o}{Markup('</strong>')}", subject="Terminacion de onu",
                                                 body_is_html=True,
                                                 # message_type='comment',
                                                 subtype_xmlid='mail.mt_comment')

                return onuid

        except Exception as e:
            raise UserError(_("Fallo al borrar onu: %s") % e)



        print(("terminated", r))
        return True


    def get_free_onuid(self, full_output, serial = None, onu_id=None):

        used_ids = dict()
        if "Onuindex" in full_output:
            for line in full_output.split("\n"):
                line = line.strip()

                print(("line", line))

                if not line or 'GPON' not in line:
                    continue

                parts = line.split()
                if parts and ':' in parts[0]:
                    try:
                        sn = parts[-1]
                        onu_id_str = parts[0].split(':')[-1]
                        used_ids[(int(onu_id_str))] = sn
                        if serial and (serial in sn): return (int(onu_id_str), True)
                    except ValueError:
                        # Ignore lines where the last part after ':' is not a valid integer
                        pass

        if (onu_id and (not used_ids.get(int(onu_id)))):
            return (onu_id, False)

        print(("used ids", used_ids))
        # Buscar el primer ID libre en el rango estándar GPON (1-128)
        for i in range(1, 129):
            if  not  used_ids.get(i, False):
                print(("i", i))
                return (i, False)

    def get_next_free_onu_id(self, pon_port_name):
        """
        Se conecta a la OLT, revisa las ONUs existentes en el puerto PON dado
        y devuelve el menor ID libre (1-128).
        :param pon_port_name: Nombre del puerto, ej: "0/1" o el formato que espere la OLT
        """
        self.ensure_one()


        try:
            with self._get_olt_connection() as conn:
                # 1. Entrar en modo configuración
                conn.execute_command("configure terminal")

                # 2. Entrar a la interfaz GPON
                # Asumimos que pon_port_name viene limpio, ej: "0/1"
                cmd_interface = f"interface gpon {pon_port_name}"
                success, clean_response, full_output = conn.execute_command(cmd_interface)
                
                if not success:
                    raise UserError(f"Error al entrar a la interfaz {pon_port_name}:\n{full_output}")

                # 3. Obtener información de ONUs
                cmd_show = "show onu info"
                success, clean_response, full_output = conn.execute_command(cmd_show)

                (onuid, s) = self.get_free_onuid(full_output)

                # 4. Salir limpiamente (opcional pero recomendado)
                conn.execute_command("exit")
                conn.execute_command("exit")

                return onuid

        except Exception as e:
            raise UserError(_("Fallo al obtener ID libre en OLT: %s") % e)

        raise UserError(_("No hay IDs de ONU libres en el puerto %s (Lleno).") % pon_port_name)

    def action_view_contracts(self):
        return self.access_point_id.action_view_contracts()
