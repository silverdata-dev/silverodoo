# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import ipaddress


class SilverIpAddress(models.Model):
    _inherit = 'silver.ip.address'

    #contract_ids = fields.One2many('silver.contract', 'ip_address_id', string="Contratos")
    contract_id = fields.Many2one("silver.contract", string="Contrato")

    used = fields.Boolean(string="Usado", compute="_compute_used")

    @api.depends("contract_id")
    def _compute_used(self):
        for s in self:
            print(("used", s.used, s.contract_id))
            s.used = (s.contract_id != None) and len(s.contract_id)>0


    def action_view_contract(self):
        """
        Opens the form view of the associated contract.
        """
        self.ensure_one()
        if self.contract_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'silver.contract',
                'view_mode': 'form',
                'res_id': self.contract_id.id,
                'target': 'current',
            }
        return {'type': 'ir.actions.act_window_close'}





    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [('name', operator, name)]

        print(("ipnamesearchh", domain))
        nodes = self.search(domain + args, limit=limit)
        return nodes.name_get()

    @api.model
    def search(self,  domain=None, offset=0, limit=None, order=None):
        ctx = self._context

        if 'order_display' in ctx:
            order = ctx['order_display']
        res = super(SilverIpAddress, self).search(
            domain,  offset=offset, limit=limit, order=order)
        print(("ipsearchh,", order, ctx, domain, res))
        return res