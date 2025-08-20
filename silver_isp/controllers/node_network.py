from odoo import http
from odoo.http import request
import json

class NodeNetwork(http.Controller):

    @http.route('/silver_isp/get_node_hierarchy', type='json', auth='user')
    def get_node_hierarchy(self, node_id, **kw):
        if not node_id:
            print("not node")
            return {'nodes': [], 'edges': []}

        node = request.env['isp.node'].browse(int(node_id))
        edges = []
        nodes = []

        # Add the main node
        nodes.append({'id': node.id, 'label': node.name, 'group': 'node'})

        # Add OLTs
        for olt in request.env['isp.olt'].search([('node_id', '=', node.id)]):
            nodes.append({'id': f'olt_{olt.id}', 'label': olt.name, 'group': 'olt'})
            edges.append({'from': node.id, 'to': f'olt_{olt.id}'})

        cores = []

        # Add Cores
        for core in request.env['isp.core'].search([('node_id', '=', node.id)]):
            cores.append(core.id)
            nodes.append({'id': f'core_{core.id}', 'label': core.name, 'group': 'core'})
            edges.append({'from': node.id, 'to': f'core_{core.id}'})
        
        # Add APs
        for ap in request.env['isp.ap'].search([('core_id', 'in', cores)]):
            nodes.append({'id': f'ap_{ap.id}', 'label': ap.name, 'group': 'ap'})
            edges.append({'from': f'core_{ap.core_id.id}', 'to': f'ap_{ap.id}'})

        for box in request.env['isp.box'].search([('node_id', '=', node.id)]):
            nodes.append({'id': f'ap_{ap.id}', 'label': ap.name, 'group': 'ap'})
            edges.append({'from': f'core_{ap.core_id.id}', 'to': f'ap_{ap.id}'})

        print(("nodes", nodes, node_id))


        return {'nodes': nodes, 'edges': edges}
