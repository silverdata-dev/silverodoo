# -*- coding: utf-8 -*-
from odoo import models, fields, api
import re
from math import radians, sin, cos, sqrt, atan2

class SilverAddress(models.Model):
    _name = 'silver.address'
    _description = 'Dirección Silver'
    _order = 'display_name'
    _rec_name = 'display_name' # Para que este sea el campo que se muestra en los Many2one

    def _get_default_country(self):
        return self.env['res.country'].search([('code', '=', 'VE')], limit=1)

    name = fields.Char(string='Dirección',compute='_compute_display_name', store=False)
    display_name = fields.Char(string="Dirección Completa", compute='_compute_display_name', store=False)
    
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

    @api.depends('street', 'building', 'house_number', 'zone_id.name', 'latitude', 'longitude')
    def _compute_display_name(self):
        for rec in self:
            print(("show ad", self.env.context, rec.latitude, rec.longitude))
            rec.display_name = rec.get_name()
            rec.name = rec.display_name


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

    def get_name(self):
        parts = [self.street, self.building, self.house_number, self.zone_id.name]
        base_name = ", ".join(filter(None, parts))

        if self.env.context.get('show_coordinates') and self.latitude and self.longitude:
           return f"{self.latitude:.5f}, {self.longitude:.5f}"
        return base_name

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

        return [(r.id, r.get_name()) for r in records]

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
            else:
                # Si no se encuentra un candidato padre, usa el search_string como la calle
                res['street'] = search_string
        
        return res


    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371000  # Radio de la Tierra en metros
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance

    @api.model
    def name_create(self, name):
        # Expresión regular para detectar coordenadas (con o sin signo)
        coord_pattern = r"^\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)\s*$"
        match = re.match(coord_pattern, name)

        if match:
            lat, lon = float(match.group(1)), float(match.group(2))
            
            # Buscar direcciones cercanas
            nearby_addresses = self.search([])
            closest_address = None
            min_distance = float('inf')

            for address in nearby_addresses:
                if address.latitude and address.longitude:
                    distance = self._haversine_distance(lat, lon, address.latitude, address.longitude)
                    if distance < min_distance:
                        min_distance = distance
                        closest_address = address
            
            vals = {'latitude': lat, 'longitude': lon}
            if closest_address and min_distance <= 20:
                # Si se encuentra una dirección a 20 metros o menos, copiar sus datos
                vals.update({
                    'street': closest_address.street,
                    'building': closest_address.building,
                    'zone_id': closest_address.zone_id.id,
                    'state_id': closest_address.state_id.id,
                    'country_id': closest_address.country_id.id,
                    'parent_id': closest_address.id,
                })

            new_address = self.create(vals)
        else:
            # Comportamiento original si no son coordenadas
            new_address = self.create({'street': name})
            
        return new_address.id, new_address.display_name
