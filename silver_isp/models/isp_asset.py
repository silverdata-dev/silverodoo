from odoo import models, fields


class IspAsset(models.Model):
    _name = 'isp.asset'
    _description = 'ISP Asset (Base Model)'
    _rec_name = 'name'


    name = fields.Char(string="Nombre")
    code = fields.Char(string="Código interno", index=True)
    asset_type = fields.Selection([
        ('olt', 'OLT'),
        ('splitter', 'Splitter'),
        ('cto', 'CTO'),
        ('core', 'Core'),
        ('node', 'Nodo'),
        ('onu', 'ONU'),
        ('manga', 'Manga'),
        ('cable', 'Cable'),
        ('ap', 'AP'),
        ('other', 'Other')
    ], default='other')



    street = fields.Char(string='Calle')
    street2 = fields.Char(string='Calle 2')
    zip = fields.Char(string='Código Postal')
    state_id = fields.Many2one('res.country.state', string='Estado')
    country_id = fields.Many2one('res.country', string='País')

    gps_lat = fields.Float(string="Latitud", digits=(16, 7))
    gps_lon = fields.Float(string="Longitud", digits=(16, 7))
    date_localization = fields.Date(string='Fecha de Geolocalización')
    date_install = fields.Date(string='Fecha de Instalación')

    brand_id = fields.Many2one('product.brand', string='Marca')
    brand_description = fields.Text(string='Descripción de Marca', related='brand_id.description')
    model = fields.Char(string='Modelo')
    astate = fields.Selection([('new','New'),('deployed','Deployed'),('maintenance','Maintenance'),('retired','Retired')], default='new')
    notes = fields.Text()
