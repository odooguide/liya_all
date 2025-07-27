from odoo import models,api,fields,_
from odoo.exceptions import UserError

class CrmLead(models.Model):
    _inherit = "crm.lead"

    project_id=fields.Many2one('project.project',string="Project")
    has_contract=fields.Boolean(string="Has Contract?",compute='_compute_contract')

    @api.depends('order_ids.confirmed_contract', 'order_ids.state','project_id')
    def _compute_contract(self):
        for lead in self:
            valid_orders = lead.order_ids.filtered(
                lambda o: o.confirmed_contract and o.state in ('sale', 'done')
            )
            lead.has_contract = bool(valid_orders)
            if lead.project_id:
                lead.has_contract=False

    def action_open_project_wizard(self):
        sale_order = self.env['sale.order'].search([
            ('opportunity_id', '=', self.id),
            ('state', 'in', ('sale', 'done'))
        ], order='id asc', limit=1)
        if not sale_order:
            raise UserError('Bu fırsata bağlı herhangi bir satış siparişi bulunamadı.')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Projeyi Oluştur ve Onayla',
            'res_model': 'sale.order.project.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': sale_order.id,
                'default_lead_id': self.id,
            },
        }

    def write(self, vals):
        if 'stage_id' in vals:
            new_stage = self.env['crm.stage'].browse(vals['stage_id'])

            if new_stage.name.lower() in ('kazanıldı', 'won') and self.has_contract:
                no_project = self.filtered(lambda lead: not lead.project_id)
                if no_project:
                    raise UserError(
                        _("Proje atanmadan Kazanıldı/Won aşamasına geçemezsiniz.")
                    )
        return super(CrmLead, self).write(vals)

    def action_open_project(self):
        self.ensure_one()
        if not self.project_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Project'),
            'res_model': 'project.project',
            'view_mode': 'form',
            'res_id': self.project_id.id,
            'target': 'current',
        }
