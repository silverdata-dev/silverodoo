# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    silver_address_id = fields.Many2one('silver.address', string='Dirección de Servicio Principal')

    @api.onchange('silver_address_id')
    def _onchange_silver_address_id(self):
        """
        Actualiza los campos de dirección nativos de Odoo cuando cambia la dirección de servicio.
        Esto asegura la compatibilidad con los módulos que dependen de los campos estándar.
        """
        if self.silver_address_id:
            addr = self.silver_address_id
            self.street = addr.street
            self.street2 = f"{addr.building}, Piso {addr.floor}, Nro {addr.house_number}"
            self.city = addr.zone_id.name if addr.zone_id else ''
            self.state_id = addr.state_id
            self.country_id = addr.country_id
            self.zip = '' # El modelo silver.address no tiene zip, se puede añadir si es necesario

    @api.model
    def create(self, vals):
        """
        Sobrescrito para asegurar la sincronización de la dirección al crear un nuevo partner.
        """
        if vals.get('silver_address_id'):
            addr = self.env['silver.address'].browse(vals['silver_address_id'])
            vals.update({
                'street': addr.street,
                'street2': f"{addr.building}, Piso {addr.floor}, Nro {addr.house_number}",
                'city': addr.zone_id.name if addr.zone_id else '',
                'state_id': addr.state_id.id,
                'country_id': addr.country_id.id,
            })
        return super(ResPartner, self).create(vals)

    def write(self, vals):
        """
        Sobrescrito para asegurar la sincronización de la dirección al actualizar un partner.
        """
        if vals.get('silver_address_id'):
            addr = self.env['silver.address'].browse(vals['silver_address_id'])
            vals.update({
                'street': addr.street,
                'street2': f"{addr.building}, Piso {addr.floor}, Nro {addr.house_number}",
                'city': addr.zone_id.name if addr.zone_id else '',
                'state_id': addr.state_id.id,
                'country_id': addr.country_id.id,
            })
        return super(ResPartner, self).write(vals)



    def name_get(self):
        """
        Método estándar de Odoo para obtener el nombre a mostrar.
        Aquí manejamos el contexto para mostrar las coordenadas.
        """
        result = []
        for rec in self:

            name = self.get_name()

            print(("ciname", self.env.context))
            if (self.env.context.get('ciname')):
                name = rec.vat + " - " + name

            if not name:
                name = rec.display_name
            result.append((rec.id, name))
        return result


    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [('name', operator, name)]

        print(("partnersearch", domain))
        nodes = self.search(domain + args, limit=limit)
        return nodes.name_get()