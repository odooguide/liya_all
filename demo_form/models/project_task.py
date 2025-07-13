from odoo import fields, api, models, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    email_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='E-mail Template',

    )

    def action_send_task_email(self):
        self.ensure_one()
        template = self.email_template_id
        ctx = dict(self.env.context or {},
                   default_model='project.task',
                   default_res_ids=[self.id],
                   default_use_template=bool(template),
                   default_template_id=template.id if template else False,
                   default_composition_mode='comment',
                   )
        return {
            'name': _('E-Posta Gönder'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'target': 'new',
            'context': ctx,
        }
