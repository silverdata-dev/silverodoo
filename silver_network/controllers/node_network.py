from odoo import http
from odoo.http import request
import json

class NodeNetwork(http.Controller):

    @http.route('/silver_network/get_node_hierarchy', type='json', auth='user')
    def get_node_hierarchy(self, node_id, **kw):
        if not node_id:
            print("not node")
            return {'nodes': [], 'edges': []}

        node = request.env['silver.node'].browse(int(node_id))
        edges = []
        nodes = []


        # Add the main node
        nodes.append({'id': f"node_{node.id}", 'label': node.name, 'group': 'node'})

        cores = []
        aps = []

        # Add Cores
        for core in request.env['silver.core'].search([('node_id', '=', node.id)]):
            cores.append(core.id)
            nodes.append({'id': f'core_{core.id}', 'label': core.name, 'group': 'core'})
            edges.append({'from': f"node_{node.id}", 'to': f'core_{core.id}'})

        # Add OLTs
        for olt in request.env['silver.olt'].search([('core_id', '=', node.id)]):
            nodes.append({'id': f'olt_{olt.id}', 'label': olt.name, 'group': 'olt'})
            edges.append({'from': f'core_{olt.core_id.id}', 'to': f'olt_{olt.id}'})


        # Add APs
        for ap in request.env['silver.ap'].search([('core_id', 'in', cores)]):
            aps.append(ap.id)
            nodes.append({'id': f'ap_{ap.id}', 'label': ap.name, 'group': 'ap'})
            edges.append({'from': f'core_{ap.core_id.id}', 'to': f'ap_{ap.id}'})


        for box in request.env['silver.box'].search([('node_id', '=', node.id)]):
            nodes.append({'id': f'box_{box.id}', 'label': box.name, 'group': 'box'})
            if box.olt_id:
                edges.append({'from': f'olt_{box.olt_id.id}', 'to': f'ap_{box.id}'})
            else:
                edges.append({'from': f'node_{node.id}', 'to': f'ap_{box.id}'})

        print(("nodes", nodes, node_id))


        return {'nodes': nodes, 'edges': edges}
