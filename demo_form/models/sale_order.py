from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    is_project_true = fields.Boolean(string='Is There Any Project?')

    project_task_ids = fields.One2many(
        comodel_name='sale.order.template.task',
        inverse_name='sale_order_id',
        string='Project Tasks',
    )

    @api.onchange('sale_order_template_id', 'order_line.product_id', 'order_line')
    def _onchange_project_task_ids(self):
        for order in self:
            order.project_task_ids = [(5, 0, 0)]
            if not order.sale_order_template_id:
                continue

            template_tasks = order.sale_order_template_id.project_task_ids
            prod_ids = order.order_line.mapped('product_id.id')
            valid_tasks = template_tasks.filtered(lambda t:
                                                  not t.optional_product_id or t.optional_product_id.id in prod_ids
                                                  )

            commands = []
            for tmpl in valid_tasks:
                vals = tmpl.copy_data()[0]
                vals.update({
                    'sale_order_id': order.id,
                    'event_date': order.wedding_date,
                })
                commands.append((0, 0, vals))

            order.project_task_ids = commands

    @api.onchange('sale_order_template_id', 'order_line.product_id','order_line')
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
                vals={
                    'sale_order_id':order.id,
                    'event_date':order.wedding_date
                }
                valid_tasks.write(vals)
            order.project_task_ids = [(6, 0, valid_tasks.ids)]
    def _add_tasks_for_product(self, product):
        """ Sadece bu product için tanımlı template task’larını kopyala ve ekle """
        self.ensure_one()
        tmpl_tasks = self.sale_order_template_id.project_task_ids.filtered(
            lambda t: t.optional_product_id and t.optional_product_id.id == product.id
        )
        for tmpl in tmpl_tasks:
            vals = tmpl.copy_data()[0]
            vals.update({
                'sale_order_id': self.id,
                'event_date': self.wedding_date,
            })
            self.project_task_ids = [(0, 0, vals)]
        return True

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

class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    def add_option_to_order(self):
        order_line = super().add_option_to_order()
        sale_order = order_line.order_id

        sale_order._add_tasks_for_product(order_line.product_id)
        return order_line