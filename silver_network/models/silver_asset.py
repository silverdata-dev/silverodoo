from odoo import models, fields, api


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
        ('nap', 'NAP'),
        ('core', 'Router'),
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




    latitude = fields.Float(
        string="Latitud Final",
        compute='_compute_final_coords',
        store=True  # ¡Clave! Fuerza el cálculo y guarda en DB
    )
    longitude = fields.Float(
        string="Longitud Final",
        compute='_compute_final_coords',
        store=True  # ¡Clave! Fuerza el cálculo y guarda en DB
    )

    n = fields.Char(string='Número')
    nn = fields.Char(string='Correlativo')


    #date_localization = fields.Date(string='Fecha de Geolocalización')
    date_install = fields.Date(string='Fecha de Instalación')

    #brand_id = fields.Many2one('product.brand', string='Marca')
    #brand_description = fields.Text(string='Descripción de Marca', related='brand_id.description')
    model = fields.Char(string='Modelo')
    #astate = fields.Selection([('new','New'),('deployed','Deployed'),('maintenance','Maintenance'),('retired','Retired')], default='new')
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

    @api.depends('silver_address_id.latitude', 'silver_address_id.longitude',
                 'gps_lon', 'gps_lat')
    def _compute_final_coords(self):
        for record in self:
            # Si tiene address_id y ese address tiene coordenadas...
            if record.silver_address_id and record.silver_address_id.latitude and record.silver_address_id.longitude:
                record.latitude = record.silver_address_id.latitude
                record.longitude = record.silver_address_id.longitude
            else:
                # Si no tiene address_id, usa las coordenadas propias
                record.latitude = record.gps_lat
                record.longitude = record.gps_lon