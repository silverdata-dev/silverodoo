from odoo import models, fields, api

class SilverZone(models.Model):
    _name = 'silver.zone'
    _description = 'Zona'
    #_table = 'isp_zone'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Code', required=True)
    
    country_id = fields.Many2one('res.country', string='Country', required=True)
    state_id = fields.Many2one('res.country.state', string='State', required=True)
    municipality_id = fields.Many2one('silver.municipality', string='Municipality')
    city_id = fields.Many2one('silver.city', string='City')
    parish_id = fields.Many2one('silver.parish', string='Parish')

    gps_top = fields.Float("GPS Norte", readonly=True)
    gps_left = fields.Float("GPS Oeste",  readonly=True)
    gps_right = fields.Float("GPS Este", readonly=True)
    gps_bottom = fields.Float("GPS Sur",  readonly=True)


    _sql_constraints = [
        ('unique_name', 'unique (name)', 'This value must be unique!')
    ]


    @api.model
    def create(self, vals):
        return super(SilverZone, self).create(vals)

    def write(self, vals):
        return super(SilverZone, self).write(vals)

