# -*- coding: utf-8 -*-

from odoo import models, fields, api

class IspRouterInterfaceWizard(models.Model):
    _name = 'isp.router.interface.wizard'
    _description = 'ISP Router Interface Wizard'

    line_ids = fields.One2many('isp.router.interface.wizard.line', 'wizard_id', string='Interfaces')
    router_id = fields.Many2one('isp.router')

class IspRouterInterfaceWizardLine(models.Model):
    _name = 'isp.router.interface.wizard.line'
    _description = 'ISP Router Interface Wizard Line'

    name = fields.Char(string='Name')
    mac_address = fields.Char(string='MAC Address')
    type = fields.Char(string='Type')
    running = fields.Boolean(string='Running')
    disabled = fields.Boolean(string='Disabled')
    comment = fields.Char(string='Comment')
    wizard_id = fields.Many2one('isp.router.interface.wizard')

class IspRouterRouteWizard(models.Model):
    _name = 'isp.router.route.wizard'
    _description = 'ISP Router Route Wizard'

    line_ids = fields.One2many('isp.router.route.wizard.line', 'wizard_id', string='Routes')
    router_id = fields.Many2one('isp.router')

class IspRouterRouteWizardLine(models.Model):
    _name = 'isp.router.route.wizard.line'
    _description = 'ISP Router Route Wizard Line'

    dst_address = fields.Char(string='Destination')
    gateway = fields.Char(string='Gateway')
    distance = fields.Integer(string='Distance')
    active = fields.Boolean(string='Active')
    static = fields.Boolean(string='Static')
    comment = fields.Char(string='Comment')
    wizard_id = fields.Many2one('isp.router.route.wizard')


class IspRouterPppActiveWizard(models.Model):
    _name = 'isp.router.ppp.active.wizard'
    _description = 'ISP Router PPP Active Wizard'

    name = fields.Char(string='Name')
    router_id = fields.Many2one('isp.router', string='Router', required=True)
    line_ids = fields.One2many('isp.router.ppp.active.wizard.line', 'wizard_id', string='Active Connections')

    #line_ids = fields.One2many('isp.router.ppp.active.wizard.line', 'wizard_id', string='Active Connections')
    #router_id = fields.Many2one('isp.router')
    ppp_speed_chart = fields.Text(string="PPP Speed Chart", readonly=True)

    @api.model
    def get_speed_data(self, wizard_id):
        # This is a placeholder for the actual data fetching logic.
        # You should replace this with your logic to get the speed data.
        import random
        return [random.randint(1, 100)]

    def action_get_active_connections(self):
        # ... (existing code)
        pass

class IspRouterPppActiveLine(models.TransientModel):
    _name = 'isp.router.ppp.active.line'
    ppp_speed_chart = fields.Text(string="PPP Speed Chart", readonly=True)

    def get_speed_data(self):
        # This is a placeholder. In a real implementation, you would fetch data from the router.
        # For now, we'll just return some random data.
        import random
        upload = [(i, random.randint(100, 500)) for i in range(20)]
        download = [(i, random.randint(500, 1500)) for i in range(20)]
        return {'upload': upload, 'download': download}

class IspRouterPppActiveWizardLine(models.Model):
    _name = 'isp.router.ppp.active.wizard.line'
    _description = 'ISP Router PPP Active Connections Wizard Line'

    name = fields.Char(string='Name')
    service = fields.Char(string='Service')
    caller_id = fields.Char(string='Caller ID')
    address = fields.Char(string='IP Address')
    uptime = fields.Char(string='Uptime')
    wizard_id = fields.Many2one('isp.router.ppp.active.wizard')

class IspRouterFirewallWizard(models.Model):
    _name = 'isp.router.firewall.wizard'
    _description = 'ISP Router Firewall Rules Wizard'

    line_ids = fields.One2many('isp.router.firewall.wizard.line', 'wizard_id', string='Firewall Rules')
    router_id = fields.Many2one('isp.router')

class IspRouterFirewallWizardLine(models.Model):
    _name = 'isp.router.firewall.wizard.line'
    _description = 'ISP Router Firewall Rules Wizard Line'

    chain = fields.Char(string='Chain')
    action = fields.Char(string='Action')
    src_address = fields.Char(string='Src. Address')
    dst_address = fields.Char(string='Dst. Address')
    protocol = fields.Char(string='Protocol')
    comment = fields.Char(string='Comment')
    disabled = fields.Boolean(string='Disabled')
    wizard_id = fields.Many2one('isp.router.firewall.wizard')

class IspRouterQueueWizard(models.Model):
    _name = 'isp.router.queue.wizard'
    _description = 'ISP Router Queues Wizard'

    line_ids = fields.One2many('isp.router.queue.wizard.line', 'wizard_id', string='Queues')
    router_id = fields.Many2one('isp.router')

class IspRouterQueueWizardLine(models.Model):
    _name = 'isp.router.queue.wizard.line'
    _description = 'ISP Router Queues Wizard Line'

    name = fields.Char(string='Name')
    target = fields.Char(string='Target')
    max_limit = fields.Char(string='Max Limit')
    burst_limit = fields.Char(string='Burst Limit')
    disabled = fields.Boolean(string='Disabled')
    comment = fields.Char(string='Comment')
    wizard_id = fields.Many2one('isp.router.queue.wizard')