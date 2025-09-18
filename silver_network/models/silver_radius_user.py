from odoo import models, fields, api, _
from odoo.exceptions import UserError
import librouteros

class SilverRadiusUser(models.Model):
    _name = 'silver.radius.user'
    _description = 'RADIUS User'

    radius_id = fields.Many2one('silver.radius', string='RADIUS Server', required=True, ondelete='cascade')
    username = fields.Char(string='Username', required=True)
    password = fields.Char(string='Password')
    profile = fields.Char(string='Profile')
    comment = fields.Text(string='Comment')
    disabled = fields.Boolean(string='Disabled', default=False)

    _sql_constraints = [
        ('username_unique', 'unique(radius_id, username)', 'Username must be unique per RADIUS server!')
    ]

    @api.model
    def create(self, vals):
        record = super(SilverRadiusUser, self).create(vals)
       # record._sync_to_mikrotik('add')
        return record

    def write(self, vals):
        res = super(SilverRadiusUser, self).write(vals)
        #self._sync_to_mikrotik('set')
        return res

    def unlink(self):
        #self._sync_to_mikrotik('remove')
        return super(SilverRadiusUser, self).unlink()

    def _get_mikrotik_api(self):
        self.ensure_one()
        radius = self.radius_id
        if not radius.ip or not radius.username or not radius.password:
            raise UserError(_("RADIUS server IP, username, and password are required for MikroTik API connection."))
        try:
            api = librouteros.connect(
                username=radius.username,
                password=radius.password,
                host=radius.ip,
                port=int(radius.port)
            )
            return api
        except Exception as e:
            raise UserError(_("Failed to connect to MikroTik API: %s") % e)

    def _sync_to_mikrotik(self, operation):
        api = self._get_mikrotik_api()
        try:
            user_path = api.path('/user-manager/user')
            if operation == 'add':
                user_path.add(
                    name=self.username,
                    password=self.password,
                    profile=self.profile or '',
                    comment=self.comment or '',
                    disabled='yes' if self.disabled else 'no'
                )
            elif operation == 'set':
                existing_user = user_path.get(name=self.username)
                if existing_user:
                    user_path.set(
                        **{'.id': existing_user[0]['.id'],
                           'password': self.password,
                           'profile': self.profile or '',
                           'comment': self.comment or '',
                           'disabled': 'yes' if self.disabled else 'no'}
                    )
                else:
                    raise UserError(_("User %s not found on MikroTik to update.") % self.username)
            elif operation == 'remove':
                existing_user = user_path.get(name=self.username)
                if existing_user:
                    user_path.remove(id=existing_user[0]['.id'])
                else:
                    raise UserError(_("User %s not found on MikroTik to remove.") % self.username)
        except Exception as e:
            raise UserError(_("MikroTik User Manager operation failed: %s") % e)
        finally:
            api.close()

    
