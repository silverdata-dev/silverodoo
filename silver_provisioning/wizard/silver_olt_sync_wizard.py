# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SilverOltSyncWizard(models.TransientModel):
    _name = 'silver.olt.sync.wizard'
    _description = 'Asistente para Sincronizar Cambios de OLT a ONUs'

    olt_id = fields.Many2one('silver.olt', string="OLT", readonly=True, required=True)
    contract_ids = fields.Many2many('silver.contract', string="Contratos Afectados", readonly=True)
    contract_count = fields.Integer(string="Número de Contratos Afectados", compute='_compute_contract_count')
    
    # Campos para mostrar los cambios pendientes
    # Estos se llenarán desde el contexto al abrir el wizard
    new_profile_dba = fields.Char(string="Nuevo Perfil DBA", readonly=True)
    new_tcont = fields.Char(string="Nuevo T-CONT", readonly=True)
    new_gemport = fields.Char(string="Nuevo GEM Port", readonly=True)
    new_service_port = fields.Char(string="Nuevo Service Port", readonly=True)

    @api.depends('contract_ids')
    def _compute_contract_count(self):
        for wizard in self:
            wizard.contract_count = len(wizard.contract_ids)

    def action_apply_changes(self):
        """
        Construye y ejecuta la lista de comandos optimizada en una sola sesión.
        """
        self.ensure_one()
        if not self.contract_ids:
            raise UserError(_("No hay contratos activos para sincronizar."))

        # Diccionario para mapear los campos del wizard a los de la OLT
        changes_to_apply = {}
        if self.new_profile_dba:
            changes_to_apply['profile_dba_internet'] = self.olt_id.profile_dba_internet
        if self.new_tcont:
            changes_to_apply['tcont'] = self.olt_id.tcont
        if self.new_gemport:
            changes_to_apply['gemport'] = self.olt_id.gemport
        if self.new_service_port:
            changes_to_apply['service_port_internet'] = self.olt_id.service_port_internet
        
        if not changes_to_apply:
            raise UserError(_("No se detectaron cambios para aplicar."))

        # --- Construcción de la Lista de Comandos Optimizada ---
        commands = ["configure terminal"]
        
        for contract in self.contract_ids:
            commands.append(f"interface gpon {contract.olt_port_id.name}")
            
            if 'profile_dba_internet' in changes_to_apply:
                commands.append(f"onu {contract.onu_pon_id} tcont {self.olt_id.tcont} dba {changes_to_apply['profile_dba_internet']}")
            
            # Aquí se añadirían los otros comandos si se implementan
            # Por ahora, nos centramos en el más común: DBA Profile
            
            commands.append("exit")

        commands.extend(["exit", "write"])

        # --- Ejecución en una Sola Sesión ---
        netdev = self.olt_id.netdev_id
        if not netdev:
            raise UserError(_("La OLT no tiene un dispositivo de red configurado."))

        log_messages = []
        try:
            with netdev._get_olt_connection() as conn:
                for command in commands:
                    success, output = conn.execute_command(command)
                    if not success:
                        log_messages.append(_("Error en comando '%s': %s") % (command, output))
                        # Decidimos continuar aunque un comando falle para no detener todo el lote
        
        except Exception as e:
            raise UserError(_("Fallo la conexión con la OLT: %s") % e)

        if log_messages:
            # Si hubo errores, los mostramos en una notificación
            error_summary = "\n".join(log_messages)
            self.env.user.notify_warning(
                title=_("Sincronización con Errores"),
                message=_("La sincronización se completó, pero ocurrieron los siguientes errores:\n%s") % error_summary,
                sticky=True # Para que el usuario deba cerrarla manualmente
            )
        else:
            self.env.user.notify_success(
                title=_("Éxito"),
                message=_("%s ONUs han sido actualizadas correctamente.") % self.contract_count
            )
            
        return {'type': 'ir.actions.act_window_close'}
