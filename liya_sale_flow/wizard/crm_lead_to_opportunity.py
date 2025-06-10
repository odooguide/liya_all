from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    def action_apply(self):
        self.ensure_one()
        lead = self.env['crm.lead'].browse(self._context.get('active_id'))
        meeting = self.env['calendar.event'].search([
            ('res_model', '=', 'crm.lead'),
            ('res_id',    '=', lead.id),
        ], limit=1)
        if not meeting:
            raise UserError(_('Planlanmış toplantı bulunmuyor.'))

        return super(Lead2OpportunityPartner, self).action_apply()
