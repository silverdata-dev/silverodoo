# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class SilverCrmMapController(http.Controller):

    @http.route('/silver_crm/get_nap_boxes', type='json', auth='user')
    def get_nap_boxes(self, node_id=None, **kwargs):
        if not node_id:
            return {'assets': []}

        # Buscar las cajas NAP que pertenecen al nodo especificado
        nap_boxes = request.env['silver.box'].search([
            ('node_id', '=', int(node_id)),
            ('latitude', '!=', 0),
            ('longitude', '!=', 0)
        ])

        # Formatear los datos para el mapa
        assets = []
        for box in nap_boxes:
            assets.append({
                'id': box.id,
                'name': box.name,
                'model': 'nap', # Modelo para el ícono
                'latitude': box.latitude,
                'longitude': box.longitude,
            })
            
        return {'assets': assets}
