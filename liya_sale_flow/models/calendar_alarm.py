from odoo import models, api,fields


class CalendarAlarm(models.Model):
    _inherit = 'calendar.alarm'

    @api.model
    def _default_24h_alarm(self):
        alarm = self.env.ref('your_module.alarm_24h_email', raise_if_not_found=False)
        return alarm and [(6, 0, [alarm.id])] or []

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