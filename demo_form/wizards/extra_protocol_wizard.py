from odoo import api, fields, models, _
import json

class ProjectDemoExtraProtocolWizard(models.TransientModel):
    _name = 'project.demo.extra.protocol.wizard'
    _description = 'Ek Protokol Görevi Onayı'

    demo_id = fields.Many2one('project.demo.form', required=True, ondelete='cascade')
    product_label = fields.Char(required=True)
    description = fields.Text()
    pending_vals_json = fields.Text(default='{}')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Odoo 18: additional_context ile gelen değerler zaten context’te
        ctx = self.env.context
        if 'pending_vals_json' in fields_list and not res.get('pending_vals_json') and ctx.get('default_pending_vals_json'):
            res['pending_vals_json'] = ctx['default_pending_vals_json']
        return res

    def _resolve_responsibles(self):
        self.ensure_one()
        demo = self.demo_id
        order = demo.project_id.sudo().reinvoiced_sale_order_id if demo.project_id else False
        users = [order.user_id.id]
        if not users and demo.project_id and demo.project_id.user_id:
            users = [demo.project_id.user_id.id]
        if not users:
            users = [self.env.user.id]
        return users

    def action_confirm_create_task(self):
        self.ensure_one()
        demo = self.demo_id
        project = demo.project_id

        # 1) Görev aç
        if project:
            task = self.env['project.task'].sudo().create({
                'project_id': project.id,
                'name': _("Ek Protokol - %s") % (self.product_label,),
                'description': self.description or "",
                'user_ids': [(6, 0, self._resolve_responsibles())],
            })

        pending = json.loads(self.pending_vals_json or '{}')
        if pending:
            demo.with_context(extra_protocol_confirmed=True).write(pending)

        if project:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.task',
                'view_mode': 'form',
                'res_id': task.id,
                'target': 'current',
            }
