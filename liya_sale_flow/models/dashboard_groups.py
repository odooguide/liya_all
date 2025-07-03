from odoo import models, fields, api

class SpreadsheetDashboardGroup(models.Model):
    _inherit = 'spreadsheet.dashboard.group'

    group_ids = fields.Many2many(
        comodel_name='res.groups',
        compute='_compute_group_ids',
        store=True,
    )

    @api.depends('dashboard_ids')
    def _compute_group_ids(self):
        score_group = self.env.ref('liya_sale_flow.group_sale_manager_custom')
        for rec in self:
            existing = rec.read(['group_ids'])[0].get('group_ids') or []
            if any(d.name == 'SCORE' for d in rec.dashboard_ids) and score_group.id not in existing:
                rec.group_ids = [(4, score_group.id)]
            else:
                rec.group_ids = [(6, 0, existing)]