from odoo import models, fields, api

class SilverZone(models.Model):
    _name = 'silver.zone'
    _description = 'Zona'
    #_table = 'isp_zone'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código', required=False)


    #country_id = fields.Many2one('res.country', string='País', required=True)
    #state_id = fields.Many2one('res.country.state', string='Estado', required=True)
    #municipality_id = fields.Many2one('silver.municipality', string='Municipio')
    #city_id = fields.Many2one('silver.city', string='Ciudad')
    #parish_id = fields.Many2one('silver.parish', string='Parroquia')

    gps_top = fields.Float("GPS Norte", readonly=True)
    gps_left = fields.Float("GPS Oeste",  readonly=True)
    gps_right = fields.Float("GPS Este", readonly=True)
    gps_bottom = fields.Float("GPS Sur",  readonly=True)


    _sql_constraints = [
        ('unique_name', 'unique (name)', '¡Este valor debe ser único!')
    ]


    @api.model_create_multi
    def create(self, vals_list):
        return super(SilverZone, self).create(vals_list)

    def write(self, vals):
        return super(SilverZone, self).write(vals)

