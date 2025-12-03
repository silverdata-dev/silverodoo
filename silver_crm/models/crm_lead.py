# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import math
import logging

_logger = logging.getLogger(__name__)

def haversine(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia en metros entre dos puntos geográficos.
    """
    # No borres nunca los comentarios en el código, ese es un precepto por siempre.
    R = 6371000  # Radio de la Tierra en metros
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) * math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # --- Campos para la integración con ISP ---
    silver_address_id = fields.Many2one('silver.address', string='Dirección de Instalación', tracking=True)
    contract_id = fields.Many2one('silver.contract', string='Contrato', tracking=True)
    plan_type_id = fields.Many2one('silver.plan.type', string='Tipo de Plan', tracking=True)
    type_service_id = fields.Many2one('silver.service.type', string='Tipo de Servicio', tracking=True)
    product_id = fields.Many2one('product.product', string='Servicio', domain="[('service_type_id', '=', type_service_id)]", tracking=True)
    node_id = fields.Many2one('silver.node', string='Nodo', tracking=True)
    box_id = fields.Many2one('silver.box', string='Caja NAP', tracking=True)
    zone_id = fields.Many2one('silver.zone', string='Zona', related="node_id.zone_id")

    def action_open_find_node_wizard(self):
        """
        Calcula los nodos cercanos, crea el wizard y sus líneas en la base de datos,
        y luego abre la vista de ese registro ya creado para evitar el error de "registro sucio".
        """
        self.ensure_one()
        
        if not self.silver_address_id or not self.silver_address_id.latitude or not self.silver_address_id.longitude:
            raise UserError(_("La dirección de instalación no tiene coordenadas. Por favor, asígnelas primero."))

        addr_lat = self.silver_address_id.latitude
        addr_lon = self.silver_address_id.longitude
        
        all_nodes = self.env['silver.node'].search([('latitude', '!=', 0), ('longitude', '!=', 0)])
        
        node_distances = []
        for node in all_nodes:
            distance = haversine(addr_lat, addr_lon, node.latitude, node.longitude)
            node_distances.append({'node': node, 'distance': distance})
            
        closest_nodes = sorted(node_distances, key=lambda k: k['distance'])[:10]
        
        line_vals = []
        for item in closest_nodes:
            line_vals.append((0, 0, {
                'node_id': item['node'].id,
                'distance': item['distance'],
            }))
        
        # Crear el wizard y sus líneas en la base de datos AHORA
        wizard = self.env['crm.find.node.wizard'].create({
            'lead_id': self.id,
            'line_ids': line_vals,
        })
        
        # Devolver la acción para abrir el wizard YA CREADO
        return {
            'name': _('Encontrar Nodos Cercanos'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.find.node.wizard',
            'view_mode': 'form',
            'res_id': wizard.id, # Apuntar al ID del registro que acabamos de crear
            'target': 'new',
        }

    def action_open_nap_map(self):
        """
        Abre la vista de mapa para seleccionar una caja NAP.
        """
        self.ensure_one()
        if not self.node_id:
            raise UserError(_("Debe seleccionar un Nodo primero."))
        if not self.silver_address_id or not self.silver_address_id.latitude or not self.silver_address_id.longitude:
            raise UserError(_("La dirección de instalación no tiene coordenadas."))

        # Devolvemos una acción de cliente, pasando los datos necesarios en el contexto
        return {
            'type': 'ir.actions.client',
            'tag': 'silver_crm.nap_map_selector', # CORREGIDO: Usar el tag correcto
            'name': _('Seleccionar Caja NAP'),
            'context': {
                'node_id': self.node_id.id,
                'customer_lat': self.silver_address_id.latitude,
                'customer_lon': self.silver_address_id.longitude,
                'lead_id': self.id, # Para saber a qué oportunidad asignar la caja
            },
        }

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for lead in self:
            if not lead.silver_address_id:
                lead.silver_address_id = lead.partner_id.silver_address_id.copy()

    @api.onchange('type_service_id')
    def _onchange_type_service_id(self):
        """
        Limpia el campo de servicio si el tipo de servicio cambia.
        """
        self.product_id = False

    def action_create_contract(self):
        """
        Crea un contrato de servicio a partir de la información del lead.
        Este método es llamado por el botón "Crear Contrato".
        """
        for lead in self:
            if not lead.partner_id:
                raise UserError(_("La oportunidad debe tener un cliente asignado para poder crear un contrato."))
            if not lead.plan_type_id or not lead.type_service_id:
                raise UserError(_("Por favor, especifique el Tipo de Plan y el Tipo de Servicio antes de crear el contrato."))
            if not lead.product_id:
                raise UserError(_("Por favor, seleccione un Servicio antes de crear el contrato."))
            if not lead.silver_address_id:
                raise UserError(_("Por favor, seleccione o cree una Dirección de Instalación."))

            # Si el cliente aún no tiene una dirección de servicio principal, se le asigna la del lead.
            if not lead.partner_id.silver_address_id:
                lead.partner_id.silver_address_id = lead.silver_address_id

            # Crear el contrato
            contract_vals = {
                'partner_id': lead.partner_id.id,
                'plan_type_id': lead.plan_type_id.id,
                'service_type_id': lead.type_service_id.id,
                'silver_address_id': lead.silver_address_id.id, # Se pasa la dirección del lead
                'origin': f"Oportunidad: {lead.name}",
                'box_id': lead.box_id.id, # Añadir la caja NAP al contrato
                # Otros valores por defecto que puedan ser necesarios
            }
            contract = self.env['silver.contract'].create(contract_vals)

            # Crear la línea de servicio en el contrato
            self.env['silver.contract.line'].create({
                'contract_id': contract.id,
                'product_id': lead.product_id.id,
                'name': lead.product_id.name,
                'quantity': 1,
                'price_unit': lead.product_id.list_price,
                'line_type': 'recurring',
            })

            # Asignar el contrato recién creado al lead
            lead.contract_id = contract.id
            
            # (Opcional) Abrir la vista del contrato recién creado
            return {
                'name': _('Contrato Creado'),
                'type': 'ir.actions.act_window',
                'res_model': 'silver.contract',
                'view_mode': 'form',
                'res_id': contract.id,
                'target': 'current',
            }
        return True

    def action_copy_address(self):
        """
        Abre una nueva vista de dirección, pre-rellenada con los datos de la dirección
        seleccionada, ideal para crear una sub-dirección (ej. otro apartamento en el mismo edificio).
        """
        self.ensure_one()
        if not self.silver_address_id:
            raise UserError(_("Primero debe seleccionar una dirección principal para poder copiarla."))

        # Usamos el método copy() con un diccionario default para indicar que es una copia
        # El contexto se usará para pre-rellenar el formulario de la nueva dirección
        context = dict(self.env.context)
        context.update({
            'default_parent_id': self.silver_address_id.id,
            'default_street': self.silver_address_id.street,
            'default_building': self.silver_address_id.building,
            'default_zone_id': self.silver_address_id.zone_id.id,
            'default_state_id': self.silver_address_id.state_id.id,
            'default_country_id': self.silver_address_id.country_id.id,
            'default_latitude': self.silver_address_id.latitude,
            'default_longitude': self.silver_address_id.longitude,
        })
        
        return {
            'name': _('Nueva Sub-Dirección'),
            'type': 'ir.actions.act_window',
            'res_model': 'silver.address',
            'view_mode': 'form',
            'target': 'new',
            'context': context,
        }

    def write(self, vals):
        """
        Sobrescrito para crear un contrato automáticamente cuando el lead se marca como ganado.
        """
        # Primero, ejecutar la lógica original del write
        res = super(CrmLead, self).write(vals)

        # Verificar si la etapa ha cambiado a "ganado"
        if 'stage_id' in vals:
            won_stages = self.env['crm.stage'].search([('is_won', '=', True)])
            for lead in self.filtered(lambda l: l.stage_id in won_stages):
                # Solo crear si los campos necesarios están llenos y no existe ya un contrato
                if lead.plan_type_id and lead.type_service_id and lead.product_id and lead.silver_address_id and not lead.contract_id:
                    _logger.info(f"Oportunidad '{lead.name}' ganada. Intentando crear contrato automáticamente.")
                    try:
                        lead.action_create_contract()
                    except Exception as e:
                        _logger.error(f"No se pudo crear el contrato para la oportunidad '{lead.name}': {e}")
                        # Opcional: registrar una actividad para que un usuario lo revise
                        lead.message_post(body=_("Error al crear el contrato automáticamente: %s") % e)
        return res

    def action_open_partner(self):
        for p in self:
          #  self.ensure_one()
            print(("openpart", p.partner_id))
            if p.partner_id:
                return {
                    'name': 'Partner',
                    'type': 'ir.actions.act_window',
                    'res_model': 'res.partner',
                    'view_mode': 'form',
                    'res_id': p.partner_id.id,
                    'target': 'new',
                }
        return False
