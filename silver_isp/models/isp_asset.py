from odoo import models, fields


class IspAsset(models.Model):
    _name = 'isp.asset'
    _description = 'ISP Asset (Base Model)'
    _rec_name = 'name'


    name = fields.Char(required=True)
    code = fields.Char(string="Código interno", required=True, index=True)
    asset_type = fields.Selection([('olt','OLT'),('splitter','Splitter'),('cto','CTO'),('onu','ONU'),('other','Other')], default='other')

    location = fields.Char(string="Ubicación")
    gps_lat = fields.Float(string="Latitud")
    gps_lon = fields.Float(string="Longitud")
    brand_id = fields.Many2one('product.brand', string='Marca')
    model = fields.Char(string='Modelo')
    state = fields.Selection([('new','New'),('deployed','Deployed'),('maintenance','Maintenance'),('retired','Retired')], default='new')
    install_date = fields.Date()
    notes = fields.Text()

