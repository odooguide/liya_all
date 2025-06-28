from odoo import fields,models

class CrmTeam(models.Model):
    _inherit='crm.team'

    wedding_team=fields.Boolean(string='Wedding Team')
    event_team=fields.Boolean(string='Event Team')

