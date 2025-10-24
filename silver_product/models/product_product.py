# -*- coding: utf-8 -*-
from odoo import models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_formview_action(self, access_uid=None):
        """
        Sobrescritura para abrir el product.template desde el stock.lot.
        Si en el contexto se pasa 'open_product_template', esta acción,
        en lugar de abrir el formulario del product.product (variante),
        abrirá el formulario del product.template (plantilla).
        """
        r = super(ProductProduct, self).get_formview_action(access_uid=access_uid)
        if self.env.context.get('open_product_template'):

            r['res_model'] = 'product.template'
            r['res_id'] = self.product_tmpl_id.id
        return r
