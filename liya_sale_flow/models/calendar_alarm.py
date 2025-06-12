from odoo import models, api

class CalendarAlarm(models.Model):
    _inherit = 'calendar.alarm'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('default_id') == 6 and 'reminder_time' in fields_list:
            res['duration'] = 24.0
        return res

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'alarm_ids' in res:
            res['alarm_ids'] = [(6, 0, [6])]
        return res