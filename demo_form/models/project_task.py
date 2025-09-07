from odoo import fields, api, models, _
from odoo.exceptions import ValidationError,UserError


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
    task_tags = fields.Char('Task Tag')
    opportunity_name=fields.Char('Çift Adı')

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

    @api.constrains('state', 'stage_id')
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

    def write(self, vals):
        if 'stage_id' in vals:
            special_users = self.env['res.users'].sudo().search([
                ('name', 'in', ['Gizem Coşkuner', 'Metin Can Çil'])
            ]).ids
            for rec in self:
                uid = self.env.uid
                if uid not in rec.user_ids.ids and uid not in special_users:
                    raise UserError("Bu aşamayı değiştirmeye yetkiniz yok.")

        res = super(ProjectTask, self).write(vals)

        if 'stage_id' in vals:
            done_names = [
                'done', 'completed', 'complete', 'finished', 'closed',
                'tamamlandı', 'tamamlandi', 'bitti', 'bitirildi', 'sonlandı', 'kapalı',
            ]
            canceled_names = [
                'cancel', 'canceled', 'cancelled',
                'iptal', 'iptal edildi', 'iptaledildi', 'vazgeçildi',
            ]
            for rec in self:
                name = (rec.stage_id.name or '').strip().lower()
                if name in done_names:
                    rec.state = '1_done'
                elif name in canceled_names:
                    rec.state = '1_canceled'
        return res