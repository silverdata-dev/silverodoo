# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import re
from math import radians, sin, cos, sqrt, atan2
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import logging

_logger = logging.getLogger(__name__)

class SilverAddress(models.Model):
    _name = 'silver.address'
    _description = 'Dirección Silver'
    _order = 'display_name'
    _rec_name = 'display_name' # Para que este sea el campo que se muestra en los Many2one

    def _get_default_country(self):
        return self.env['res.country'].search([('code', '=', 'VE')], limit=1)

    # El display_name se almacena para búsquedas y ordenamiento.
    # name_get se encargará de la visualización final dependiente del contexto.
    name = fields.Char(string='Dirección', compute='_compute_display_name', store=False)
    display_name = fields.Char(string="Dirección Completa", compute='_compute_display_name', store=False)
    
    parent_id = fields.Many2one('silver.address', string='Dirección Padre')
    
    # Información Geográfica
    country_id = fields.Many2one('res.country', string='País', default=_get_default_country)
    state_id = fields.Many2one('res.country.state', string='Estado')
    zone_id = fields.Many2one('silver.zone', string='Zona')
    
    # Dirección Detallada
    street = fields.Char(string='Calle')
    street2 = fields.Char(string='Referencia / Cruce') # Nuevo campo
    building = fields.Char(string='Edificio/Casa')
    floor = fields.Char(string='Piso')
    house_number = fields.Char(string='Número de Casa/Apartamento')
    zip = fields.Char(string='Código Postal')
    
    # Coordenadas
    latitude = fields.Float(string='Latitud', digits=(10, 7))
    longitude = fields.Float(string='Longitud', digits=(10, 7))

    # Nuevo campo unificado para visualización/edición de coordenadas
    lat_long_display = fields.Char(
        string='Coordenadas',
        compute='_compute_lat_long_display', 
        inverse='_inverse_lat_long_display',
        help="Formato: Latitud, Longitud (ej. 10.4806, -66.9036)"
    )

    # Campo auxiliar para migraciones o pegado rápido
    raw_address_search = fields.Char(string="Texto para Búsqueda/Migración", 
                                     help="Escribe aquí la dirección completa para intentar autocompletar.")

    @api.depends('latitude', 'longitude')
    def _compute_lat_long_display(self):
        for rec in self:
            if rec.latitude or rec.longitude:
                # Usamos .5f para consistencia visual, aunque el float tenga más
                rec.lat_long_display = f"{rec.latitude}, {rec.longitude}"
            else:
                rec.lat_long_display = ""

    def _inverse_lat_long_display(self):
        for rec in self:
            if not rec.lat_long_display:
                rec.latitude = 0.0
                rec.longitude = 0.0
                continue
            
            try:
                # Intentar limpiar y separar por coma
                parts = rec.lat_long_display.split(',')
                if len(parts) == 2:
                    lat = float(parts[0].strip())
                    lon = float(parts[1].strip())
                    rec.latitude = lat
                    rec.longitude = lon
                else:
                    # Intento alternativo por si pegan algo raro, pero lo básico es coma
                    # Si falla, no escribimos o lanzamos warning (mejor no bloquear UX)
                    pass
            except ValueError:
                # Si no son números válidos, ignorar
                pass

    @api.onchange('lat_long_display')
    def _onchange_lat_long_display(self):
        """
        Permite que el widget de mapa (que escucha latitude/longitude)
        se actualice inmediatamente cuando el usuario cambia el texto.
        """
        if not self.lat_long_display:
            self.latitude = 0.0
            self.longitude = 0.0
            return

        try:
            # Reutilizamos la misma lógica robusta de limpieza
            # Aceptamos coma o espacios como separador básico
            parts = re.split(r'[,\s]+', self.lat_long_display.strip())
            # Filtramos partes vacías
            parts = [p for p in parts if p]
            
            if len(parts) >= 2:
                self.latitude = float(parts[0])
                self.longitude = float(parts[1])
        except ValueError:
            # Si el usuario escribe basura, no rompemos la UI, simplemente no actualizamos los floats
            pass

    def _clean_l10n_name(self, name, prefixes):
        """
        Método auxiliar para limpiar nombres de municipios/parroquias.
        Ej: "Municipio Libertador" -> "Libertador"
        """
        if not name: return ""
        for prefix in prefixes:
            # Busca el prefijo al inicio, insensible a mayúsculas, seguido opcionalmente de punto y espacios
            pattern = r"^\s*" + prefix + r"\.?\s+(.*)"
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return name.strip()

    @api.model
    def get_address_from_coords(self, lat, lon):
        """
        Método llamado desde el Widget JS. 
        Realiza geocodificación inversa para obtener detalles de dirección
        a partir de coordenadas.
        Devuelve un diccionario listo para ser usado por el cliente web.
        """
        if not lat or not lon:
            return {}

        geolocator = Nominatim(user_agent="silver_odoo_widget_reverse_v1")
        vals = {}

        try:
            # Reverse Geocoding
            location = geolocator.reverse((lat, lon), exactly_one=True, addressdetails=True, timeout=10)
            
            if location:
                data = location.raw.get('address', {})
                
                # 1. Componentes de texto
                # Intentamos varios campos posibles de OSM para la calle
                vals['street'] = (data.get('road') or 
                                  data.get('pedestrian') or 
                                  data.get('highway') or 
                                  data.get('residential') or
                                  # Si no hay calle, a veces viene en 'suburb' o 'neighbourhood' como fallback
                                  data.get('suburb') or 
                                  '')
                                  
                vals['house_number'] = data.get('house_number', '')
                vals['zip'] = data.get('postcode', '')
                vals['building'] = data.get('building', '')
                vals['floor'] = data.get('level') or data.get('floor') or '' # Añadido para el piso

                # 2. Relacionales (Buscamos los IDs directamente aquí)
                
                # País
                country_code = data.get('country_code')
                if country_code:
                    country = self.env['res.country'].search([('code', '=', country_code.upper())], limit=1)
                    if country:
                        vals['country_id'] = country.id

                # Estado
                state_name = data.get('state')
                if state_name and vals.get('country_id'):
                    state = self.env['res.country.state'].search([
                        ('country_id', '=', vals['country_id']),
                        ('name', 'ilike', state_name)
                    ], limit=1)
                    if state:
                        vals['state_id'] = state.id
                
                # 3. Lógica L10N VE (Municipios/Parroquias) con Auto-Creación
                # Verificamos si los modelos existen en el entorno (silver_l10n_ve_base)
                if 'res.country.municipality' in self.env and vals.get('state_id'):
                    # Mapeo OSM -> Venezuela: 'county' suele ser Municipio, 'municipality' suele ser Parroquia
                    raw_mun = data.get('county')
                    raw_par = data.get('municipality')
                    
                    # Limpieza
                    clean_mun = self._clean_l10n_name(raw_mun, ['Municipio', 'Mun'])
                    clean_par = self._clean_l10n_name(raw_par, ['Parroquia', 'Pq'])
                    
                    # Gestión Municipio
                    if clean_mun:
                        Mun = self.env['res.country.municipality']
                        mun_rec = Mun.search([
                            ('name', '=ilike', clean_mun), 
                            ('state_id', '=', vals['state_id'])
                        ], limit=1)
                        
                        if not mun_rec:
                            _logger.info(f"Creando Municipio desde Mapa: {clean_mun}")
                            mun_rec = Mun.create({
                                'name': clean_mun, 
                                'code': clean_mun.upper().replace(' ', '_'),
                                'state_id': vals['state_id']
                            })

                        vals['municipality_id'] = mun_rec.id
                        
                        # Gestión Parroquia (Solo si tenemos municipio)
                        if clean_par:
                            Par = self.env['res.country.parish']
                            par_rec = Par.search([
                                ('name', '=ilike', clean_par), 
                                ('municipality_id', '=', mun_rec.id)
                            ], limit=1)
                            
                            if not par_rec:
                                _logger.info(f"Creando Parroquia desde Mapa: {clean_par}")
                                par_rec = Par.create({
                                    'name': clean_par,
                                    'code': clean_par.upper().replace(' ', '_'),
                                    'municipality_id': mun_rec.id
                                })
                            
                            vals['parish_id'] = par_rec.id

                # Zona (Opcional, si tienes lógica para esto)
                zone_name = data.get('suburb') or data.get('neighbourhood') or data.get('city')
                if zone_name:
                    zone = self.env['silver.zone'].search([('name', 'ilike', zone_name)], limit=1)
                    if zone:
                        vals['zone_id'] = zone.id

        except Exception as e:
            _logger.warning(f"Error en reverse geocoding: {e}")
            # Si falla, devolvemos vacío y el usuario tendrá que llenar a mano
        
        return vals

    def _parse_address_heuristics(self, raw_text):
        """
        Extrae componentes específicos (Edificio, Casa, Apto, Cruce) del texto usando RegEx.
        Retorna: (vals, clean_text)
        vals: diccionario con los campos extraídos para Odoo.
        clean_text: texto limpio para enviar al geocodificador.
        """
        vals = {}
        clean_text = raw_text

        # Definición de Patrones (Regex)
        # IMPORTANTE: El orden importa. 
        # Extraemos primero lo más específico (Piso, Apto) para evitar que 'Edificio' se lo trague.
        patterns = {
            'floor': [
                r"(?:Piso|P\.?\s*B\.?|P-)\s*([0-9A-Za-z]+)(?=,|$)", # P-1, PB, Piso 5
                r"Piso\s*([0-9]+)",
                r"piso\s*([0-9]+)",
            ],
            'house_number': [
                r"(?:Casa|Nro\.?|No\.?|#)\s*([a-zA-Z0-9\s-]+)(?=,|$)",
                r"(?:Apto\.?|Apartamento|Oficina|Local)\s+([a-zA-Z0-9\s\.-]+?)(?=,|$)"
            ],
            'building': [
                r"(?:Edificio|Edif\.?|Residencia|Res\.?|Torre|Conjunto|C\.C\.|Centro Comercial)\s+([a-zA-Z0-9\s\.-]+?)(?=,|$)",
            ],
            'street2': [
                r"(?:Cruce con|Esquina|Esq\.?|Transversal)\s+([a-zA-Z0-9\s\.-]+?)(?=,|$)",
                r"\b(?:con|y)\s+(?:Calle|Avda\.?|Avenida)?\s*([a-zA-Z0-9\s\.-]+?)(?=,|$)",
                r"\/\s*(?:Calle|Avda\.?|Avenida)?\s*([a-zA-Z0-9\s\.-]+?)(?=,|$)",
                r"\b(?:c\s|c\.)\s*(?:Calle|Avda\.?|Avenida)?\s*([a-zA-Z0-9\s\.-]+?)(?=,|$)"
            ]
        }

        # Iterar y extraer
        for field, regex_list in patterns.items():
            for pattern in regex_list:
                match = re.search(pattern, clean_text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    # Si ya extrajimos algo para este campo, concatenar (ej: Casa 4, Apto 2)
                    if vals.get(field):
                        vals[field] += f", {value}"
                    else:
                        vals[field] = value
                    
                    # Remover del texto para limpiar la búsqueda
                    # Reemplazamos por una coma para mantener la estructura si estaba en medio
                    clean_text = re.sub(pattern, ",", clean_text, flags=re.IGNORECASE)

        # Limpieza final del texto de búsqueda
        # Eliminar comas dobles, espacios extra, y conectores colgantes al final
        clean_text = re.sub(r",\s*,", ",", clean_text)
        clean_text = re.sub(r"\s+", " ", clean_text).strip(" ,.-")
        
        # Quitar " y " o " con " si quedaron al final por haber extraído lo que seguía
        clean_text = re.sub(r"\s+(y|con|c\.)$", "", clean_text, flags=re.IGNORECASE)

        return vals, clean_text

    def action_parse_and_geolocate(self):
        """
        Toma el texto de raw_address_search:
        1. Extrae heurísticamente componentes (Edificio, Casa)
        2. Limpia el texto
        3. Consulta OSM con el texto limpio
        4. Rellena los campos
        """
        self.ensure_one()
        if not self.raw_address_search:
            return

        # 1. Parsing Heurístico
        extracted_vals, clean_search_query = self._parse_address_heuristics(self.raw_address_search)
        
        _logger.info(f"Geolocalizando. Original: '{self.raw_address_search}' -> Limpio:'{clean_search_query}'")

        # 2. Configurar Geocodificador
        geolocator = Nominatim(user_agent="silver_odoo_migration_v1")

        def try_geocode(query):
            try:
                # addressdetails=True es clave para discriminar ciudad/estado
                return geolocator.geocode(query, addressdetails=True, timeout=10)
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                _logger.warning(f"Timeout/Error con Geocodificador para '{query}': {e}")
                return None

        # 3. Estrategia de Búsqueda (Retry Logic) con el texto LIMPIO
        location = None
        
        # Intento 1: Texto limpio completo
        location = try_geocode(clean_search_query)

        # Intento 2: Simplificación progresiva (quitar partes desde la izquierda)
        if not location and ',' in clean_search_query:
            parts = [p.strip() for p in clean_search_query.split(',') if p.strip()]
            
            for i in range(1, len(parts)):
                reduced_query = ", ".join(parts[i:])
                if not reduced_query: continue
                
                _logger.info(f"Reintentando geocodificación con: {reduced_query}")
                location = try_geocode(reduced_query)
                if location:
                    break

        if not location:
            _logger.warning(f"Dirección no encontrada tras reintentos: {clean_search_query}")
            # Aun si no encontramos coords, guardamos lo que pudimos extraer por regex
            if extracted_vals:
                self.write(extracted_vals)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Parcialmente encontrado',
                        'message': 'Se extrajeron datos (Edif/Casa) pero no se encontraron coordenadas exactas.',
                        'type': 'warning',
                    }
                }
            return

        # 4. Extraer Datos de Geolocalización
        data = location.raw.get('address', {})
        vals = {
            'latitude': location.latitude,
            'longitude': location.longitude,
        }
        
        # Combinar con los datos extraídos heurísticamente
        vals.update(extracted_vals)

        # Calle / Avenida (Solo si no extrajimos nada mejor, o concatenamos)
        # OSM devuelve 'road'. Si extrajimos 'street2' (cruce), OSM nos da la principal.
        osm_road = data.get('road') or data.get('pedestrian') or data.get('highway') or data.get('residential')
        if osm_road:
            vals['street'] = osm_road
        elif not vals.get('street'): 
            # Si OSM no da calle y regex tampoco, usar el texto limpio como fallback
            vals['street'] = clean_search_query.split(
            ','
            )[0]

        # Campos numéricos/postales de OSM (si no los tenemos ya)
        if data.get('house_number') and not vals.get('house_number'):
            vals['house_number'] = data.get('house_number')
        
        if data.get('postcode') and not vals.get('zip'):
            vals['zip'] = data.get('postcode')
        
        if data.get('level') or data.get('floor') and not vals.get('floor'): # También de OSM
            vals['floor'] = data.get('level') or data.get('floor')

        # 5. Búsqueda de Relacionales (País y Estado)
        country_code = data.get('country_code') # Ej: 've'
        if country_code:
            country = self.env['res.country'].search([('code', '=', country_code.upper())], limit=1)
            if country:
                vals['country_id'] = country.id

        state_name = data.get('state') # Ej: 'Lara'
        if state_name and vals.get('country_id'):
            state = self.env['res.country.state'].search([
                ('country_id', '=', vals['country_id']),
                ('name', 'ilike', state_name)
            ], limit=1)
            if state:
                vals['state_id'] = state.id
        
        # 6. Lógica L10N VE (Municipios/Parroquias) con Auto-Creación
        # Copiamos la misma lógica del get_address_from_coords
        if 'res.country.municipality' in self.env and vals.get('state_id'):
            raw_mun = data.get('county')
            raw_par = data.get('municipality')
            
            clean_mun = self._clean_l10n_name(raw_mun, ['Municipio', 'Mun'])
            clean_par = self._clean_l10n_name(raw_par, ['Parroquia', 'Pq'])
            
            if clean_mun:
                Mun = self.env['res.country.municipality']
                mun_rec = Mun.search([
                    ('name', '=ilike', clean_mun), 
                    ('state_id', '=', vals['state_id'])
                ], limit=1)
                
                if not mun_rec:
                    _logger.info(f"Creando Municipio desde Parseo: {clean_mun}")
                    mun_rec = Mun.create({
                        'name': clean_mun, 
                        'code': clean_mun.upper().replace(' ', '_'),
                        'state_id': vals['state_id']
                    })
                
                vals['municipality_id'] = mun_rec.id
                
                if clean_par:
                    Par = self.env['res.country.parish']
                    par_rec = Par.search([
                        ('name', '=ilike', clean_par), 
                        ('municipality_id', '=', mun_rec.id)
                    ], limit=1)
                    
                    if not par_rec:
                        _logger.info(f"Creando Parroquia desde Parseo: {clean_par}")
                        par_rec = Par.create({
                            'name': clean_par,
                            'code': clean_par.upper().replace(' ', '_'),
                            'municipality_id': mun_rec.id
                        })
                    
                    vals['parish_id'] = par_rec.id

        # Zona / Municipio / Ciudad (Mapeo a silver.zone si aplica)
        potential_zone_name = data.get('suburb') or data.get('neighbourhood') or data.get('city')
        if potential_zone_name:
            zone = self.env['silver.zone'].search([('name', 'ilike', potential_zone_name)], limit=1)
            if zone:
                vals['zone_id'] = zone.id

        # 7. Guardar
        self.write(vals)

        return True
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Éxito',
                'message': f'Dirección discriminada y geolocalizada: {location.latitude}, {location.longitude}',
                'type': 'success',
            }
        }

    @api.depends('street', 'building', 'house_number', 'zone_id.name', 'latitude', 'longitude', 'street2', 'floor') # Agregado street2 y floor a depends
    def _compute_display_name(self):
        """
        Calcula el nombre base almacenado de la dirección.
        """
        for rec in self:
            # Si la dirección no tiene componentes legibles pero tiene coordenadas, mostramos coordenadas.
            # has_readable_address = any([rec.street, rec.building, rec.house_number, rec.zone_id])

            print(("dname", rec.street, rec.building, rec.house_number, rec.zone_id.name, rec.latitude, rec.longitude)) # User's print statement
            if self.env.context.get('show_coordinates') :
                base_name = f"{rec.latitude:.5f}, {rec.longitude:.5f}"
            else:
                # Agregando street2 y floor a las partes del nombre de visualización
                parts = [rec.street, rec.street2, rec.building, rec.floor, rec.house_number, rec.zone_id.name]
                base_name = ", ".join(filter(None, parts))

            rec.display_name = base_name
            rec.name = base_name

    def name_get(self):
        """
        Método estándar de Odoo para obtener el nombre a mostrar.
        Aquí manejamos el contexto para mostrar las coordenadas.
        """
        result = []
        for rec in self:
            print(("show ad", self.env.context, rec.latitude, rec.longitude)) # User's print statement
            
            if self.env.context.get('show_coordinates') : #and rec.latitude and rec.longitude:
                # Sin paréntesis, como solicitaste.
                name = f"{rec.latitude:.5f}, {rec.longitude:.5f}"
            else:
                # Agregando street2 y floor a las partes del nombre de visualización
                parts = [rec.street, rec.street2, rec.building, rec.floor, rec.house_number, rec.zone_id.name]
                name = ", ".join(filter(None, parts))

            # Si no hay datos de dirección legible, usamos el display_name
            if not name:
                name = rec.display_name
            result.append((rec.id, name))
        return result

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
                ('latitude', '>=' , lat_min), ('latitude', '<=', lat_max),
                ('longitude', '>=' , lng_min), ('longitude', '<=', lng_max),
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
                res.update({
                    'parent_id': parent_candidate.id,
                    'street': parent_candidate.street,
                    'building': parent_candidate.building,
                    'zone_id': parent_candidate.zone_id.id,
                    'state_id': parent_candidate.state_id.id,
                    'country_id': parent_candidate.country_id.id,
                    'latitude': parent_candidate.latitude,
                    'longitude': parent_candidate.longitude,
                })
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
            print(("lat,long", lat, lon))
            nearby_addresses = self.search([('latitude', '!=', 0), ('longitude', '!=', 0)])
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
        # name_create debe devolver el resultado de name_get
        return new_address.name_get()[0]
