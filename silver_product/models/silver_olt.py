from odoo import models, fields, _
from odoo.exceptions import UserError


class SilverOlt(models.Model):
    _inherit = 'silver.olt'

    stock_lot_id = fields.Many2one(
        'stock.lot',
        string='Equipo (Serie/Lote)',
        related='netdev_id.stock_lot_id',
        readonly=False,
        store=True,
    )
   # brand_name = fields.Char(string='Marca', related='stock_lot_id.brand_name', readonly=True, store=True)
   # model_name = fields.Char(string='Modelo', related='stock_lot_id.model_name', readonly=True, store=True)
    brand_id = fields.Many2one('product.brand', string="Marca", related='stock_lot_id.brand_id', readonly=True, store=True)
    brand_logo = fields.Binary(related='brand_id.logo', string='Logo de la Marca')
    hardware_model_id = fields.Many2one('silver.hardware.model', string='Modelo', related='stock_lot_id.hardware_model_id', readonly=True, store=True)

    software_version = fields.Char(string='Versión de Software', related='stock_lot_id.software_version', readonly=True, store=True)
    firmware_version = fields.Char(string='Firmware Version', related='stock_lot_id.firmware_version', readonly=True, store=True)
    serial_number = fields.Char(string='Serial Number', related='stock_lot_id.serial_number', readonly=True, store=True)

    onu_profile_ids = fields.Many2many('silver.onu.profile', 'silver_olt_profile', 'olt_id', 'profile_id',  string='ONU Profiles')

    def check_profile_on_olt( self):
        """Checks if the ONU profile exists on the selected OLT."""
        profile_id = self.env.context.get('params')['id']
        profile = self.env['silver.onu.profile'].browse(profile_id)

        commands = [
#            'enable',
            'configure terminal',
            'show profile onu name  {}'.format(profile.name),
            'exit'

        ]

        print(("olt", self, self.env.context))

        output = self.execute_olt_commands( commands)
        print(("show profiles", output))

        # Simple check: if the output contains the profile name, it likely exists.
        # This might need to be made more robust based on actual OLT output.
        if self.name in output:
            message = f"Profile '{profile.name}' seems to exist on OLT '{profile.name}'.\n\n{output}"
            title = "Profile Found"
        else:
            message = f"Profile '{profile.name}' not found or an error occurred on OLT '{profile.name}'.\n\n{output}"
            title = "Profile Not Found"

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'sticky': True,  # Keep the message visible until the user closes it
            }
        }

    def add_profile_to_olt(self):
        """Adds the ONU profile to the selected OLT using the predefined commands."""
        #olt_id = self.env.context.get('active_id')
        #olt = self.env['silver.olt'].browse(olt_id)
        profile_id = self.env.context.get('params')['id']
        profile = self.env['silver.onu.profile'].browse(profile_id)
        output_log = ''

        try:

            with self.netdev_id._get_olt_connection() as conn:

                output_log= self.check_and_create_onu_profile(conn, profile, "")

            return output_log
        except (ConnectionError, UserError) as e:
            raise UserError(f"Operation failed:\n{e}\n\nLog:\n{output_log}")
        except Exception as e:
            # Catching unexpected errors
            raise UserError(f"An unexpected error occurred: {e}\n\nLog:\n{output_log}")



        # If we reach here, the commands were sent without raising an exception.
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Profile creation commands sent to OLT %s.', self.name),
                'type': 'success',
            }
        }


    def execute_olt_commands(self,  commands):
        """Helper function to connect to an OLT and execute a list of commands."""
        for olt in self:
            print(("olt", olt, olt.netdev_id))
          #  self.ensure_one()
            output_log = ""
            try:

                with olt.netdev_id._get_olt_connection() as conn:
                    for command in commands:
                        success, response, output = conn.execute_command(command)
                        output_log += f"$ {command}\n{output}\n"
                        if not success:
                            # You might want to check for specific non-critical errors here
                            # For now, any failure stops the process.
                            raise UserError(f"Error executing command '{command}':\n{output}")
                return output_log
            except (ConnectionError, UserError) as e:
                raise UserError(f"Operation failed:\n{e}\n\nLog:\n{output_log}")
            except Exception as e:
                # Catching unexpected errors
                raise UserError(f"An unexpected error occurred: {e}\n\nLog:\n{output_log}")
