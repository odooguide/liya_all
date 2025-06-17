from odoo import api,fields,models,_
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit='sale.order'

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

    def action_project_create(self):
        self.ensure_one()

        if self.project_id:
            return True

        seq_num = self.env['ir.sequence'].next_by_code('sale.order.project') or '0000'
        today = fields.Date.context_today(self)
        date_str = today.strftime('%Y-%m-%d')
        partner_slug = self.partner_id.name.replace(' ', '-')
        project_name = f"D{seq_num}-{date_str}-{partner_slug}"

        vals = {
            'name': project_name,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id.id or self.env.uid,
            'allow_billable': True,
            'privacy_visibility': 'portal',
            'sale_order_id': self.id,
        }

        project = self.env['project.project'].create(vals)

        self.project_id = project.id

        self.is_project_true=True

        return True