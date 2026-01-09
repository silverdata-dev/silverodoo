from odoo import models, api

import requests
import json
from odoo import models, api



class SyncMixin(models.AbstractModel):
    _name = 'sync.mixin'
    _description = 'Detecta cambios y encola la sincronización'

    @api.model_create_multi
    def create(self, vals_list):
        records = super(SyncMixin, self).create(vals_list)
        if not self.env.context.get('is_sync_job'):
            for rec in records:
                print(("createrec", rec))
                # Encolamos el envío
                rec.with_delay()._enqueue_sync('create')
        return records

    def write(self, vals):
        res = super(SyncMixin, self).write(vals)
        if not self.env.context.get('is_sync_job'):
            for rec in self:
                print(("writerec", rec))
                rec.with_delay()._enqueue_sync('write')
        return res

    def _enqueue_sync(self, action):
        """Prepara los datos para el Job"""
        # Obtenemos el XML_ID del registro
        xml_id_data = self.get_external_id().get(self.id)
        if not xml_id_data:
            # Si no tiene XML_ID (es nuevo), lo generamos
            xml_id = f"__export__.{self._table}_{self.id}"
            self.env['ir.model.data'].create({
                'module': '__export__',
                'name': f"{self._table}_{self.id}",
                'model': self._name,
                'res_id': self.id,
            })
        else:
            xml_id = xml_id_data

        # Campos que queremos enviar (puedes filtrarlos)
        vals = self.copy_data()[0]

    #    print(("enqueue", vals))

        # Disparamos el Job de envío real
        self.env['sync.sender.job'].with_delay().send_to_destination(
            self._name, xml_id, vals
        )