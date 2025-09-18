from odoo import models, fields, api

class SilverSplitter(models.Model):
    _name = 'silver.splitter'
    _description = 'Splitter de Conexion'
    #_table = 'isp_splitter'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    _inherits = {'silver.asset': 'asset_id'}

    asset_id = fields.Many2one('silver.asset', required=True, ondelete="cascade")

    name = fields.Char(string='Nombre', readonly=True, copy=False, default='New')
    capacity_splitter = fields.Selection([("1:1","1:1"), ("1:2","1:2"), ("1:4","1:4"), ("1:8", "1:8"), ("1:16","1:16")], string='Capacidad')
    port_splitter = fields.Char(string='Puerto Splitter Primario')
    type_splitter = fields.Selection([('1', 'Primario'), ('2', 'Secundario')], string='Tipo', required=True)
    splitter_id = fields.Many2one('silver.splitter', string='Spliter Principal')
    olt_card_port_id = fields.Many2one('silver.olt.card.port', string='Puerto Tarjeta OLT', required=True, ondelete='cascade')

    box_count = fields.Integer(string='Conteo Cajas', compute='_compute_box_count')
    contracts_count = fields.Integer(string='Conteo Cajas', compute='_compute_contracts_count')



    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='splitter',
        store=True,
        readonly=False
    )

    @api.model
    def create(self, vals):
        if vals.get('olt_card_port_id'):
            port = self.env['silver.olt.card.port'].browse(vals['olt_card_port_id'])
            if port.exists():
                splitter_type = vals.get('type_splitter')
                prefix = 'SPL1' if splitter_type == '1' else 'SPL2'
                splitter_count = self.search_count([
                    ('olt_card_port_id', '=', port.id),
                    ('type_splitter', '=', splitter_type)
                ])
                vals['name'] = f"{port.name}/{prefix}{splitter_count + 1}"
        return super(SilverSplitter, self).create(vals)

    def write(self, vals):
        # Determine the new name if the parent port or the type changes
        if 'olt_card_port_id' in vals or 'type_splitter' in vals:
            for record in self:
                port = self.env['silver.olt.card.port'].browse(vals.get('olt_card_port_id', record.olt_card_port_id.id))
                splitter_type = vals.get('type_splitter', record.type_splitter)
                if port.exists():
                    prefix = 'SPL1' if splitter_type == '1' else 'SPL2'
                    # When writing, we need to be careful about the count.
                    # If we are changing the type of an existing record, we should get a new number.
                    splitter_count = self.search_count([
                        ('olt_card_port_id', '=', port.id),
                        ('type_splitter', '=', splitter_type)
                    ])
                    # If we are changing the type, the current record is not yet of the new type
                    if 'type_splitter' in vals and record.type_splitter != vals['type_splitter']:
                         record.name = f"{port.name}/{prefix}{splitter_count + 1}"
                    # If we are just changing the parent port
                    elif 'olt_card_port_id' in vals:
                         record.name = f"{port.name}/{prefix}{splitter_count + 1}"
                    # Otherwise, don't change the name unless necessary
        return super(SilverSplitter, self).write(vals)

    def _compute_box_count(self):
        for record in self:
            record.box_count = self.env['silver.box'].search_count([('splitter_id', '=', record.id)])

    def _compute_contracts_count(self):
        for record in self:
            record.contracts_count = self.env['silver.contract'].search_count([('splitter_id', '=', record.id)])

    def create_box(self):
        self.ensure_one()
        new_box = self.env['silver.box'].create({
#            'name': f"Box for {self.name}",
            'splitter_id': self.id,
        })
        return {
            'name': 'Box Creada',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.box',
            'view_mode': 'form',
            'res_id': new_box.id,
            'target': 'current',
        }

    def action_view_boxes(self):
        self.ensure_one()
        return {
            'name': 'Cajas NAP',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.box',
            'view_mode': 'tree,form',
            'domain': [('splitter_id', '=', self.id)],
            'context': {'default_splitter_id': self.id},
            'target': 'current',
        }

    def action_view_contracts(self):
        self.ensure_one()
        return {
            'name': 'Contratos',
            'type': 'ir.actions.act_window',
            'res_model': 'silver.contract',
            'view_mode': 'tree,form',
            'domain': [('splitter_id', '=', self.id)],
            'context': {'default_splitter_id': self.id},
            'target': 'current',
        }
