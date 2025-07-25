from odoo import models, api, fields, _
from odoo.exceptions import UserError


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    event_place=fields.Selection([('online','Online'),('on_field','On Field')], string='Event Place')
    categ_name=fields.Char('Event Name',compute='_compute_categ_name')
    meeting_date=fields.Date(string='Meeting Date',compute='_compute_meeting_date',store=True)



    @api.depends('start')
    def _compute_meeting_date(self):
        """
        Compute the meeting_date as the date portion of the event's start datetime.
        """
        for rec in self:
            if rec.start:
                # Convert the stored string to a datetime, then take its date
                dt = fields.Datetime.from_string(rec.start)
                rec.meeting_date = dt.date()
            else:
                rec.meeting_date = False

    @api.depends('categ_ids')
    def _compute_categ_name(self):
        if self.categ_ids:
            self.categ_name=self.categ_ids[0].name
        else:
            self.categ_name=False
    ##### Defaul Get #####
    @api.model
    def _default_attendees(self):
        """ When active_model is res.partner, the current partners should be attendees """
        partners = self.env.user.partner_id
        active_id = self._context.get('active_id')
        if self._context.get('active_model') == 'res.partner' and active_id and active_id not in partners.ids:
            partners |= self.env['res.partner'].browse(active_id)
        return partners

    partner_ids = fields.Many2many(
        'res.partner', 'calendar_event_res_partner_rel',
        string='Attendees', default=_default_attendees,
        domain=[('employee_ids', '!=', False)]
    )

    @api.model
    def default_get(self, fields_list):
        """ Adding 24 Hour Reminder every event"""
        res = super(CalendarEvent, self).default_get(fields_list)
        if 'alarm_ids' in fields_list:
            alarm = self.env.ref('liya_sale_flow.alarm_24h_email', raise_if_not_found=False)
            if alarm:
                res['alarm_ids'] = [(6, 0, [alarm.id])]
        return res



    @api.model_create_multi
    def create(self, vals_list):
        events = super().create(vals_list)

        if not self.env.context.get('skip_sale_tagging'):
            categ_model = self._fields['categ_ids'].comodel_name
            sale_cat = self.env[categ_model].search(
                [('name', '=', events.activity_ids.activity_type_id.display_name)], limit=1
            )
            if sale_cat:
                for ev in events:
                    ev.write({'categ_ids': [(4, sale_cat.id)]})

        return events

    # def write(self, vals):
    #     if 'categ_ids' in vals and not self.env.context.get('skip_categ_check'):
    #         for ev in self:
    #             ev.check_categ_ids(vals)
    #     return super().write(vals)

    # def check_categ_ids(self, vals):
    #     if isinstance(vals, list):
    #         for v in vals:
    #             if not v.get('categ_ids'):
    #                 raise UserError(_('Lütfen en az bir etiket seçin.'))
    #     else:
    #         if not vals.get('categ_ids'):
    #             raise UserError(_('Lütfen en az bir etiket seçin.'))
    #     return True
