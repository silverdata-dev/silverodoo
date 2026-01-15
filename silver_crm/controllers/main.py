# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class SilverCrmController(http.Controller):

    @http.route('/silver_crm/get_nap_boxes', type='jsonrpc', auth='user')
    def get_nap_boxes(self, node_id=None, **kwargs):
        if not node_id:
            return {'assets': []}

        # Buscar las cajas NAP que pertenecen al nodo especificado
        nap_boxes = request.env['silver.box'].search([
            ('node_id', '=', int(node_id)),
            ('latitude', '!=', 0),
            ('longitude', '!=', 0)
        ])

        print(("boxes", nap_boxes))

        # Formatear los datos para el mapa
        assets = []
        for box in nap_boxes:
            assets.append({
                'id': box.id,
                'name': box.name,
                'model': 'box',  # Modelo para el ícono
                'latitude': box.latitude,
                'longitude': box.longitude,
            })

        return {'assets': assets}

    @http.route('/silver_crm/select_nap_box', type='json', auth='user')
    def select_nap_box(self, box_id, lead_id):
        """
        Controller endpoint to assign a NAP box to a lead.
        """
        if not box_id or not lead_id:
            return {'status': 'error', 'message': 'Missing box_id or lead_id'}

        Lead = request.env['crm.lead']
        Box = request.env['silver.box']

        lead = Lead.browse(int(lead_id))
        box = Box.browse(int(box_id))

        if lead.exists() and box.exists():
            lead.write({'box_id': box.id})
            return {'status': 'success', 'message': 'NAP box assigned successfully'}
        else:
            return {'status': 'error', 'message': 'Lead or Box not found'}