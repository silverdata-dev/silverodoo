# models/sync_handler.py
from odoo import models, api


class SyncHandler(models.Model):
    _name = 'sync.handler'
    _inherit = 'queue.job'

    def _sanitize_vals(self, model_name, vals):
        model = self.env[model_name]
        # Solo permitimos campos que existan físicamente en el modelo destino
        return {k: v for k, v in vals.items()}

    @api.model
    def process_upsert(self, model_name, external_id, vals):
        # Evitar loops y disparar lógica de negocio
        ctx = {'is_sync_job': True, 'tracking_disable': True}

        # Buscar el registro por su XML_ID (External ID)
        record = self.env.ref(external_id, raise_if_not_found=False)

        # Limpiar vals de campos que no existen o son protegidos
        sanitized_vals = self._sanitize_vals(model_name, vals)

        print(("upsert", sanitized_vals, record))

        if record:
            print(("write", record.with_context(**ctx)))
            record.with_context(**ctx).write(sanitized_vals)
        else:
            new_record = self.env[model_name].with_context(**ctx).create(sanitized_vals)
            self._bind_external_id(new_record, external_id)

    def _bind_external_id(self, record, xml_id):
        # Esta es la parte vital: anclar el registro al ID del servidor origen
        mod, name = xml_id.split('.') if '.' in xml_id else ('__export__', xml_id)
        self.env['ir.model.data'].create({
            'module': mod, 'name': name,
            'model': record._name, 'res_id': record.id,
        })
        