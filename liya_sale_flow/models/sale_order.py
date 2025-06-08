from odoo import models,api,fields,_
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit='sale.order'

    project_task_ids = fields.Many2many(
        comodel_name='sale.order.template.task',
        string='Project Tasks',
        compute='_compute_project_task_ids',
        readonly=True,
    )

    @api.depends('sale_order_template_id', 'order_line.product_id')
    def _compute_project_task_ids(self):
        for order in self:
            if not order.sale_order_template_id:
                order.project_task_ids = False
                continue
            tasks = order.sale_order_template_id.project_task_ids
            prod_ids = order.order_line.mapped('product_id.id')

            valid = tasks.filtered(
                lambda t: not t.optional_product_id
                          or t.optional_product_id.id in prod_ids
            )
            order.project_task_ids = valid


    def action_confirm(self):

        res = super().action_confirm()
        for order in self:
            if order.sale_order_template_id:
                if not order.project_id:
                    raise UserError(_(
                        "Sipariş %s için proje oluşturulmamış. "
                        "Önce bir proje atanmalı."
                    ) % order.name)
                for tmpl in order.project_task_ids:
                    self.env['project.task'].create({
                        'project_id': order.project_id.id,
                        'name': tmpl.name,
                        'description': tmpl.description,
                        'stage_id': tmpl.stage_id.id,
                        'user_ids': [(6, 0, tmpl.user_ids.ids)],
                    })
        return res