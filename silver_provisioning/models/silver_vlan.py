# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SilverVlan(models.Model):
    _inherit = 'silver.vlan'
    contract_ids = fields.One2many('silver.contract', 'vlan_id', string="OLT")


    @api.model
    def default_get(self, fields):
        # 1. Llamar al método base para obtener los defaults estándar
        res = super(SilverVlan, self).default_get(fields)

        # 2. Obtener el ID que pasaste desde el Many2one
        id_a_incluir = self.env.context.get('default_core_id')

        if id_a_incluir :
            # 3. Construir el comando Many2many para añadir/reemplazar
            # Comando (6, 0, [IDs]): Reemplaza cualquier valor y pone solo [id_a_incluir]
            # Si el M2M está vacío, simplemente lo añade.

            # NOTA: Odoo requiere que los IDs estén en una lista.
            res['core_ids'] = [(6, 0, [id_a_incluir])]
            core = self.env['silver.core'].browse(id_a_incluir)
            if core.node_id:
                res['node_id'] = core.node_id.id

        return res