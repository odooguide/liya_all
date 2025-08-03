from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_project_true = fields.Boolean(string='Is There Any Project?')
    project_task_ids = fields.One2many(
        'sale.project.task',
        'sale_order_id',
        string='Project Tasks',
    )

    @api.onchange('sale_order_template_id')
    def _onchange_sale_template_task(self):
        if not self.sale_order_template_id:
            self.project_task_ids = [(5, 0, 0)]
            self.is_project_true = False
            return

        new_tasks = []
        for tmpl in self.sale_order_template_id.project_task_ids:
            if tmpl.optional_product_id:
                continue

            new_tasks.append((0, 0, {
                'name': tmpl.name,
                'description': tmpl.description,
                'stage_id': tmpl.stage_id.id,
                'planned_date': tmpl.planned_date,
                'deadline_date': tmpl.deadline_date,
                'date_line': tmpl.date_line,
                'days': tmpl.days,
                'user_ids': [(6, 0, tmpl.user_ids.ids)],
                'email_template_id': tmpl.email_template_id.id,
                'communication_type': tmpl.communication_type,
                'event_date': tmpl.event_date,
            }))

        self.project_task_ids = [(5, 0, 0)] + new_tasks
        self.is_project_true = bool(new_tasks)

    @api.onchange('order_line')
    def _onchange_order_line_task(self):
        for order in self:
            if not order.sale_order_template_id:
                return

            current_products = order.order_line.mapped('product_id')
            template_tasks = order.sale_order_template_id.project_task_ids

            to_remove = order.project_task_ids.filtered(
                lambda t: t.optional_product_id and t.optional_product_id not in current_products
            )
            remove_cmds = [(2, t.id) for t in to_remove]

            preserve = order.project_task_ids.filtered(
                lambda t: t.optional_product_id and t.optional_product_id in current_products
            )
            preserve_cmds = [(4, t.id) for t in preserve]

            preserved_prods = preserve.mapped('optional_product_id')
            to_add = template_tasks.filtered(
                lambda tmpl: tmpl.optional_product_id
                             and tmpl.optional_product_id in current_products
                             and tmpl.optional_product_id not in preserved_prods
            )
            add_cmds = []
            for tmpl in to_add:
                add_cmds.append((0, 0, {
                    'name': tmpl.name,
                    'description': tmpl.description,
                    'stage_id': tmpl.stage_id.id,
                    'planned_date': tmpl.planned_date,
                    'deadline_date': tmpl.deadline_date,
                    'date_line': tmpl.date_line,
                    'days': tmpl.days,
                    'user_ids': [(6, 0, tmpl.user_ids.ids)],
                    'email_template_id': tmpl.email_template_id.id,
                    'optional_product_id': tmpl.optional_product_id.id,
                    'communication_type': tmpl.communication_type,
                    'event_date': tmpl.event_date,
                }))

            order.project_task_ids = remove_cmds + preserve_cmds + add_cmds
            order.project_task_ids._onchange_deadline_date()

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

    @api.onchange('wedding_date')
    def _onchange_wedding_date(self):
        for rec in self:
            if rec.project_task_ids:
                rec.project_task_ids._onchange_deadline_date()


class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    def add_option_to_order(self):
        order_line = super(SaleOrderOption, self).add_option_to_order()
        self.order_id._onchange_order_line_task()
        return order_line
