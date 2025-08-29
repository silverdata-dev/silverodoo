from odoo import models, fields, api

class IspZone(models.Model):
    _name = 'isp.zone'
    _description = 'Zona'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    name = fields.Char(string='Nombre', readonly=False, copy=False)
    gps_top = fields.Float("GPS Norte", compute='_compute_gps', readonly=True)
    gps_left = fields.Float("GPS Oeste", compute='_compute_gps', readonly=True)
    gps_right = fields.Float("GPS Este", compute='_compute_gps', readonly=True)
    gps_bottom = fields.Float("GPS Sur", compute='_compute_gps', readonly=True)

    assets = fields.One2many('isp.asset', 'zone_id', string='Elementos')

    node_count = fields.Integer(string='Nodos', compute='_compute_counts')

    _sql_constraints = [
        ('unique_name', 'unique (name)', 'This value must be unique!')
    ]


    @api.model
    def create(self, vals):
        return super(IspZone, self).create(vals)

    def write(self, vals):
        return super(IspZone, self).write(vals)



    def _compute_counts(self):
        for record in self:
            record.node_count = self.env['isp.asset'].search_count([('zone_id', '=', record.id), ('asset_type', '=', 'node')])

    def _compute_gps(self):
        for record in self:
            lats = [asset.gps_lat for asset in record.assets if asset.gps_lat]
            lons = [asset.gps_lon for asset in record.assets if asset.gps_lon]

            if lats:
                record.gps_top = min(lats)
                record.gps_bottom = max(lats)
            else:
                record.gps_top = 0.0
                record.gps_bottom = 0.0

            if lons:
                record.gps_left = min(lons)
                record.gps_right = max(lons)
            else:
                record.gps_left = 0.0
                record.gps_right = 0.0

    def create_core(self):
        self.ensure_one()
        new_node = self.env['isp.node'].create({
            #'name': f"Core for {self.name}",
            'zone_id': self.id,
        })
        return {
            'name': 'Nodo Creado',
            'type': 'ir.actions.act_window',
            'res_model': 'isp.node',
            'view_mode': 'form',
            'res_id': new_node.id,
            'target': 'current',
        }