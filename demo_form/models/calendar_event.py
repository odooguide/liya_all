from odoo import models, api


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.model
    def _get_activity_excluded_models(self):
        excluded_models = super()._get_activity_excluded_models()
        
        if self.env.context.get('skip_demo_meeting_activity'):
            excluded_models = list(excluded_models)
            excluded_models.append('project.project')
        
        return excluded_models