# controllers/main.py
from odoo import http
from odoo.http import request

class GenericSyncController(http.Controller):
    @http.route('/sync/v1/data', type='jsonrpc', auth='none', methods=['POST'], csrf=False)
    def receive_sync(self, **kwargs):
        # 1. Seguridad básica: Token en el header o params

        print(("receivesync", kwargs))
        token = request.httprequest.headers.get('X-Sync-Token')
        if token != "TU_TOKEN_SECRETO":
            return {"error": "Conexión no autorizada"}

        model = kwargs.get('model')
        external_id = kwargs.get('external_id')
        vals = kwargs.get('vals')

        # 2. Encolar la tarea
        request.env['sync.handler'].with_delay().process_upsert(model, external_id, vals)
        return {"status": "accepted"}