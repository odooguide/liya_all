from odoo import models, api,fields,_
from odoo.exceptions import UserError

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.model
    def _default_partners(self):
        """ When active_model is res.partner, the current partners should be attendees """
        partners = self.env.user.partner_id
        active_id = self._context.get('active_id')
        if self._context.get('active_model') == 'res.partner' and active_id and active_id not in partners.ids:
                partners |= self.env['res.partner'].browse(active_id)
        return partners
    
    partner_ids = fields.Many2many(
        'res.partner', 'calendar_event_res_partner_rel',
        string='Attendees', default=_default_partners,
        domain=[('employee_ids', '!=', False)]
        )

    @api.model
    def default_get(self, fields_list):
        res = super(CalendarEvent, self).default_get(fields_list)
        if 'alarm_ids' in fields_list:
            alarm = self.env.ref('liya_sale_flow.alarm_24h_email', raise_if_not_found=False)
            if alarm:
                res['alarm_ids'] = [(6, 0, [alarm.id])]
        return res

    # @api.model
    # def create(self, vals):
    #     if not vals.get('categ_ids'):
    #         raise UserError(_('Lütfen en az bir etiket seçin.'))
    #     return super(CalendarEvent, self).create(vals)

    @api.model_create_multi
    def create(self, vals_list):
        events = super(CalendarEvent, self).create(vals_list)

        categ_model = self._fields['categ_ids'].comodel_name
        sale_cat = self.env[categ_model].search(
            [('name', '=', 'Satış Toplantısı')], limit=1
        )
        if not sale_cat:
            return events

        for event in events:
            if any(act.activity_type_id.id == 14 for act in event.activity_ids):
                event.write({'categ_ids': [(4, sale_cat.id)]})

        return events

    def write(self, vals):
        if 'categ_ids' in vals:
            res = super(CalendarEvent, self).write(vals)
            for event in self:
                if not event.categ_ids:
                    raise UserError(_('Lütfen en az bir etiket seçin.'))
            return res
        return super(CalendarEvent, self).write(vals)