from odoo import models, fields

class IspSplitter(models.Model):
    _name = 'isp.splitter'
    _description = 'Splitter de Conexion'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    _inherits = {'isp.asset': 'asset_id'}

    asset_id = fields.Many2one('isp.asset', required=True, ondelete="cascade")

    name_sppliter = fields.Char(string='Nombre')
    capacity_splitter = fields.Selection([], string='Capacidad')
    port_splitter = fields.Char(string='Puerto Splitter Primario')
    type_splitter = fields.Selection([('1', 'Primario'), ('2', 'Secundario')], string='Tipo')
    splitter_id = fields.Many2one('isp.splitter', string='Spliter Principal')
    olt_card_port_id = fields.Many2one('isp.olt.card.port', string='Puerto Tarjeta OLT')

    box_count = fields.Integer(string='Conteo Cajas', compute='_compute_box_count')
    contracts_count = fields.Integer(string='Conteo Cajas', compute='_compute_contracts_count')



    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='splitter',
        store=True,
        readonly=False
    )

    def _compute_box_count(self):
        for record in self:
            record.box_count = self.env['isp.box'].search_count([('splitter_id', '=', record.id)])

    def _compute_contracts_count(self):
        for record in self:
            record.contracts_count = self.env['isp.contract'].search_count([('splitter_id', '=', record.id)])

    def create_box(self):
        self.ensure_one()
        new_box = self.env['isp.box'].create({
            'name': f"Box for {self.name}",
            'splitter_id': self.id,
        })
        return {
            'name': 'Box Creada',
            'type': 'ir.actions.act_window',
            'res_model': 'isp.box',
            'view_mode': 'form',
            'res_id': new_box.id,
            'target': 'current',
        }
