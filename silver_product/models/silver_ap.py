from odoo import models, fields

class SilverAp(models.Model):
    _inherit = 'silver.ap'

    stock_lot_id = fields.Many2one(
        'stock.lot',
        string='Equipo (Serie/Lote)',
        related='netdev_id.stock_lot_id',
        readonly=False,
        store=True,
    )
    brand_name = fields.Char(string='Marca', related='stock_lot_id.product_id.product_brand_id.name', readonly=True, store=True)
    model_name = fields.Char(string='Modelo', related='stock_lot_id.product_id.model', readonly=True, store=True)
    software_version = fields.Char(string='Versión de Software', related='stock_lot_id.software_version', readonly=True, store=True)
    firmware_version = fields.Char(string='Firmware Version', related='stock_lot_id.firmware_version', readonly=True, store=True)
    serial_number = fields.Char(string='Serial Number', related='stock_lot_id.serial_number', readonly=True, store=True)