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

    silver_address_id = fields.Many2one('silver.address', string='Dirección')

    zone_id = fields.Many2one('silver.zone', string='Zona', related='silver_address_id.zone_id')
    #parent_id = fields.Many2one('silver.asset', string='Parent')
    #root_id = fields.Many2one('silver.asset', string='Root')

    #street = fields.Char(string='Calle')
    #street2 = fields.Char(string='Calle 2')
    #zip = fields.Char(string='Codigo Postal')
    #state_id = fields.Many2one('res.country.state', string='Estado')
    #country_id = fields.Many2one('res.country', string='País', default=lambda self: self._get_default_country())
    #place = fields.Char(string='Edificio/Zona')
    gps_lat = fields.Float(string="Latitud", digits=(16, 7), readonly=False)
    gps_lon = fields.Float(string="Longitud", digits=(16, 7), readonly=False)

    n = fields.Char(string='Número')
    nn = fields.Char(string='Correlativo')


    #date_localization = fields.Date(string='Fecha de Geolocalización')
    date_install = fields.Date(string='Fecha de Instalación')

    #brand_id = fields.Many2one('product.brand', string='Marca')
    #brand_description = fields.Text(string='Descripción de Marca', related='brand_id.description')
    model = fields.Char(string='Modelo')
    astate = fields.Selection([('new','New'),('deployed','Deployed'),('maintenance','Maintenance'),('retired','Retired')], default='new')
    notes = fields.Text()

    #
    # core_ids = fields.One2many('silver.core', 'asset_id', string='Cores')
    #olt_ids = fields.One2many('silver.olt', 'asset_id', string='OLTs')
    #box_ids = fields.One2many('silver.box', 'asset_id', string='Boxes')
    #ap_ids = fields.One2many('silver.ap', 'asset_id', string='APs')
    #cable_ids = fields.One2many('silver.cable', 'asset_id', string='Cables')
    #splice_closure_ids = fields.One2many('silver.splice_closure', 'asset_id', string='Splice Closures')
    #splitter_ids = fields.One2many('silver.splitter', 'asset_id', string='Splitters')
    #post_ids = fields.One2many('silver.post', 'asset_id', string='Posts')
    #node_ids = fields.One2many('silver.node', 'asset_id', string='Nodos')


    line_string_wkt = fields.Char(string='LineString WKT')
    color = fields.Char(string="Color")

    def _get_default_country(self):
        return self.env['res.country'].search([('code', '=', 'VE')], limit=1)