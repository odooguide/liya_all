from odoo import models, api,fields,_
from odoo.exceptions import UserError
class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.model
    def default_get(self, fields_list):
        res = super(CalendarEvent, self).default_get(fields_list)
        if 'alarm_ids' in fields_list:
            alarm = self.env.ref('liya_sale_flow.alarm_24h_email', raise_if_not_found=False)
            if alarm:
                res['alarm_ids'] = [(6, 0, [alarm.id])]
        return res

    @api.model
    def create(self, vals):
        if not vals.get('categ_ids'):
            raise UserError(_('Lütfen en az bir etiket seçin.'))
        return super(CalendarEvent, self).create(vals)

    def write(self, vals):
        if 'categ_ids' in vals:
            res = super(CalendarEvent, self).write(vals)
            for event in self:
                if not event.categ_ids:
                    raise UserError(_('Lütfen en az bir etiket seçin.'))
            return res
        return super(CalendarEvent, self).write(vals)