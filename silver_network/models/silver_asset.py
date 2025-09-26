from odoo import models, fields


class SilverAsset(models.Model):
    _name = 'silver.asset'
    #_table = 'isp_asset'
    _description = 'ISP Asset (Base Model)'
    _rec_name = 'name'


    name = fields.Char(string="Nombre")
    code = fields.Char(string="Codigo interno")
    asset_type = fields.Selection([
        ('olt', 'OLT'),
        ('splitter', 'Splitter'),
        ('cto', 'CTO'),
        ('core', 'Core'),
        ('node', 'Nodo'),
        ('onu', 'ONU'),
        ('manga', 'Manga'),
        ('cable', 'Cable'),
        ('post', 'Poste'),
        ('ap', 'AP'),
        ('other', 'Other')
    ], default='other')

    _sql_constraints = [
        ('unique_code', 'unique (code)', 'This value must be unique!')
    ]

    zone_id = fields.Many2one('silver.zone', string='Zona')
    parent_id = fields.Many2one('silver.asset', string='Parent')
    root_id = fields.Many2one('silver.asset', string='Root')

    street = fields.Char(string='Calle')
    street2 = fields.Char(string='Calle 2')
    zip = fields.Char(string='Codigo Postal')
    state_id = fields.Many2one('res.country.state', string='Estado')
    country_id = fields.Many2one('res.country', string='País', default=lambda self: self._get_default_country())
    place = fields.Char(string='Edificio/Zona')
    n = fields.Char(string='Número')
    nn = fields.Char(string='Correlativo')

    gps_lat = fields.Float(string="Latitud", digits=(16, 7), readonly=False)
    gps_lon = fields.Float(string="Longitud", digits=(16, 7), readonly=False)
    date_localization = fields.Date(string='Fecha de Geolocalización')
    date_install = fields.Date(string='Fecha de Instalación')

    #brand_id = fields.Many2one('product.brand', string='Marca')
    #brand_description = fields.Text(string='Descripción de Marca', related='brand_id.description')
    model = fields.Char(string='Modelo')
    astate = fields.Selection([('new','New'),('deployed','Deployed'),('maintenance','Maintenance'),('retired','Retired')], default='new')
    notes = fields.Text()


    line_string_wkt = fields.Char(string='LineString WKT')
    color = fields.Char(string="Color")

    def _get_default_country(self):
        return self.env['res.country'].search([('code', '=', 'VE')], limit=1)