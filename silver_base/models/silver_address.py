# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SilverAddress(models.Model):
    _name = 'silver.address'
    _description = 'Dirección Silver'
    _order = 'name'

    def _get_default_country(self):
        return self.env['res.country'].search([('code', '=', 'VE')], limit=1)

    name = fields.Char(string="Dirección Completa", compute='_compute_display_address', store=True)
    
    parent_id = fields.Many2one('silver.address', string='Dirección Padre')
    
    # Información Geográfica
    country_id = fields.Many2one('res.country', string='País', default=_get_default_country)
    state_id = fields.Many2one('res.country.state', string='Estado')
    zone_id = fields.Many2one('silver.zone', string='Zona')
    
    # Dirección Detallada
    street = fields.Char(string='Calle')
    building = fields.Char(string='Edificio/Casa')
    floor = fields.Char(string='Piso')
    house_number = fields.Char(string='Número de Casa/Apartamento')
    
    # Coordenadas
    latitude = fields.Float(string='Latitud', digits=(10, 7))
    longitude = fields.Float(string='Longitud', digits=(10, 7))

    @api.depends('street', 'building', 'house_number', 'zone_id.name')
    def _compute_display_address(self):
        for rec in self:
            parts = [rec.street, rec.building, rec.house_number, rec.zone_id.name]
            rec.name = ", ".join(filter(None, parts))

    def _onchange_zone_id(self):
        if self.zone_id:
            self.country_id = self.zone_id.country_id
            self.state_id = self.zone_id.state_id

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if self.parent_id:
            self.country_id = self.parent_id.country_id
            self.state_id = self.parent_id.state_id
            self.zone_id = self.parent_id.zone_id
            self.street = self.parent_id.street
            self.building = self.parent_id.building
            self.latitude = self.parent_id.latitude
            self.longitude = self.parent_id.longitude

    @api.onchange('latitude', 'longitude')
    def _onchange_coordinates(self):
        if self.latitude and self.longitude:
            # Definir el rango de búsqueda
            lat_min, lat_max = self.latitude - 0.0002, self.latitude + 0.0002
            lng_min, lng_max = self.longitude - 0.0002, self.longitude + 0.0002

            # El ID del registro actual, si existe
            current_id = self._origin.id if isinstance(self.id, models.NewId) else self.id

            # Buscar una dirección cercana que no sea la misma
            domain = [
                ('latitude', '>=', lat_min),
                ('latitude', '<=', lat_max),
                ('longitude', '>=', lng_min),
                ('longitude', '<=', lng_max),
            ]
            if current_id:
                domain.append(('id', '!=', current_id))
            
            potential_parent = self.search(domain, limit=1)

            if potential_parent:
                self.parent_id = potential_parent

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Permite buscar direcciones por calle, edificio o nombre de la zona.
        """
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', ('street', operator, name), ('building', operator, name), ('zone_id.name', operator, name)]
        
        records = self.search(domain + args, limit=limit)
        return records.name_get()

    @api.model
    def default_get(self, fields_list):
        """
        Al crear una nueva dirección desde el campo Many2one (ej: en un contacto),
        si el texto introducido coincide con una dirección existente,
        la establece como padre y copia sus datos geográficos.
        """
        res = super(SilverAddress, self).default_get(fields_list)
        search_string = self.env.context.get('default_name')

        if search_string:
            # Busca la dirección que mejor coincida para usarla como padre
            parent_candidate = self.search([
                '|', '|',
                ('street', 'ilike', search_string),
                ('building', 'ilike', search_string),
                ('zone_id.name', 'ilike', search_string)
            ], limit=1)

            if parent_candidate:
                res['parent_id'] = parent_candidate.id
                res['street'] = parent_candidate.street
                res['building'] = parent_candidate.building
                res['zone_id'] = parent_candidate.zone_id.id
                res['state_id'] = parent_candidate.state_id.id
                res['country_id'] = parent_candidate.country_id.id
                res['latitude'] = parent_candidate.latitude
                res['longitude'] = parent_candidate.longitude
        
        return res
