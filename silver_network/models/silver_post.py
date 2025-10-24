from odoo import models, fields, api

class SilverPost(models.Model):
    _name = 'silver.post'
    #_table = 'isp_post'
    _description = 'Post de Conexion'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    _inherits = {'silver.asset': 'asset_id'}

    asset_id = fields.Many2one('silver.asset', required=True, ondelete="cascade")

    name = fields.Char(string='Nombre', related='asset_id.name', readonly=False, copy=False)
    port_post = fields.Char(string='Puerto Post Primario')
    type_post = fields.Selection([('P', 'Poste')], string='Tipo', required=False, default="P")

    latitude = fields.Float(string="Latitud", digits=(16, 7), related='asset_id.latitude', readonly=False, required=True)
    longitude = fields.Float(string="Longitud", digits=(16, 7), related='asset_id.longitude', readonly=False, required=True)


    asset_type = fields.Selection(
        related='asset_id.asset_type',
        default='post',
        store=True,
        readonly=False
    )

    @api.model
    def create(self, vals):
        if vals.get('olt_card_port_id'):


            post_type = vals.get('type_post', 'P')

            post_count = self.search_count([
                ('type_post', '=', post_type)
            ])
            vals['name'] = f"P{post_count + 1}"
        return super(SilverPost, self).create(vals)

    def write(self, vals):
        # Determine the new name if the parent port or the type changes
        for record in self:
            pass
        return super(SilverPost, self).write(vals)

