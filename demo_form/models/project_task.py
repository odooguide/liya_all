from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    email_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='E-mail Template',

    )
    communication_type = fields.Selection(selection=[
        ('mail', 'E-Mail'),
        ('phone', 'Whatsapp'),
    ],
        string='Communication Type',
       )
    task_tags=fields.Char('Task Tag')

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

    @api.constrains('state','stage_id')
    def _check_demo_task_event(self):
        for task in self:
            if (
                    task.name == 'Demo Randevu Oluşturma'
                    and task.state == '1_done'
                    and not task.project_id.event_ids
            ):
                raise ValidationError(_(
                    '“Demo Randevu Oluşturma” görevini "Tamamlandı" durumuna getirebilmek için '
                    'Demo tarihi belirlenmelidir.'
                ))
            if (
                    task.name == 'Demo Randevu Oluşturma'
                    and task.stage_id.name == 'Done'
                    and not task.project_id.event_ids
            ):
                raise ValidationError(_(
                    '“Demo Randevu Oluşturma” görevini "Tamamlandı" durumuna getirebilmek için '
                    'Demo tarihi belirlenmelidir.'
                ))
