from odoo import models, api
from odoo.tools import config

import requests
import json
from odoo import models, api


class SyncSenderJob(models.Model):
    _name = 'sync.sender.job'
    _inherit = 'queue.job'

    @api.model
    def send_to_destination(self, model_name, xml_id, vals):


        r=config.get('remote')
        url = f"{r}/sync/v1/data"


        print(("destination", r, url))

        headers = {
            'X-Sync-Token': 'TU_TOKEN_SECRETO',
            'Content-Type': 'application/json'
        }
        payload = {
            "jsonrpc": "2.0",
            "params": {
                "model": model_name,
                "external_id": xml_id,
                "vals": vals
            }
        }

       # open("/tmp/re","a").write(str(("send to destination", model_name, xml_id, vals)))

        def default(obj):
            """Default JSON serializer."""
            import calendar, datetime

          #  print(("default", obj))

            if isinstance(obj, datetime.datetime):
                return str(obj)
#                if obj.utcoffset() is not None:
#                    obj = obj - obj.utcoffset()
#                millis = int(
#                    calendar.timegm(obj.timetuple()) * 1000 +
#                    obj.microsecond / 1000
#                )
#                return millis
            return obj
            # raise TypeError('Not sure how to serialize %s' % (obj,))

        try:
            response = requests.post(url, data=json.dumps(payload, default=default), headers=headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            # queue_job reintentará automáticamente si lanzas una excepción
            raise Exception(f"Fallo en la conexión mística: {e}")
