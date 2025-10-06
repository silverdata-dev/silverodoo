# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SilverAddress(models.Model):
    _name = 'silver.address'
    _description = 'Silver Address'

    name = fields.Char(string="Description", compute='_compute_display_address', store=True)
    
    parent_id = fields.Many2one('silver.address', string='Parent Address')
    
    # Geographic Info
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one('res.country.state', string='State')
    municipality_id = fields.Many2one('silver.municipality', string='Municipality')
    city_id = fields.Many2one('silver.city', string='City')
    parish_id = fields.Many2one('silver.parish', string='Parish')
    zone_id = fields.Many2one('silver.zone', string='Zone')
    
    # Detailed Address
    street = fields.Char(string='Street')
    building = fields.Char(string='Building/House Name')
    floor = fields.Char(string='Floor')
    house_number = fields.Char(string='House Number')
    
    # Coordinates
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))

    @api.depends('street', 'house_number', 'city_id', 'country_id')
    def _compute_display_address(self):
        for rec in self:
            parts = [rec.street, rec.house_number, rec.city_id.name, rec.country_id.name]
            rec.name = ", ".join(filter(None, parts))

    @api.onchange('zone_id')
    def _onchange_zone_id(self):
        if self.zone_id:
            self.country_id = self.zone_id.country_id
            self.state_id = self.zone_id.state_id
            self.municipality_id = self.zone_id.municipality_id
            self.city_id = self.zone_id.city_id
            self.parish_id = self.zone_id.parish_id

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if self.parent_id:
            self.country_id = self.parent_id.country_id
            self.state_id = self.parent_id.state_id
            self.municipality_id = self.parent_id.municipality_id
            self.city_id = self.parent_id.city_id
            self.parish_id = self.parent_id.parish_id
            self.zone_id = self.parent_id.zone_id
            self.street = self.parent_id.street
            self.building = self.parent_id.building
            self.latitude = self.parent_id.latitude
            self.longitude = self.parent_id.longitude
