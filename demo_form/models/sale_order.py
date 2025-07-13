from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    is_project_true = fields.Boolean(string='Is There Any Project?')

    project_task_ids = fields.Many2many(
        comodel_name='sale.order.template.task',
        inverse_name='sale_order_id',
        string='Project Tasks',
    )

    @api.onchange('sale_order_template_id', 'order_line.product_id')
    def _onchange_project_task_ids(self):
        for order in self:
            if not order.sale_order_template_id:
                order.project_task_ids = [(5, 0, 0)]
                continue

            tasks = order.sale_order_template_id.project_task_ids
            prod_ids = order.order_line.mapped('product_id.id')

            valid_tasks = tasks.filtered(lambda t:
                                         not t.optional_product_id or
                                         t.optional_product_id.id in prod_ids
                                         )
            if valid_tasks:
                valid_tasks.write({'sale_order_id': order.id})
            order.project_task_ids = [(6, 0, valid_tasks.ids)]

    def action_open_project_wizard(self):
        self.ensure_one()
        if self.opportunity_id.stage_id.name not in ('Won', 'Kazanıldı'):
            raise UserError(_('Fırsat kazanıldı olmadan proje oluşturamazsın.'))
        if not self.project_task_ids:
            raise UserError(_('Görev girmeden proje oluşturamazsın..'))

        return {
            'name': 'Proje Oluştur',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.project.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,

            },
        }
