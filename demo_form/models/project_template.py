from odoo import fields, models, _, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    event_ids = fields.One2many(
        'calendar.event', 'res_id',
        string='Calendar Events',
        domain=[('res_model', '=', 'project.project')]
    )

    next_event_id = fields.Many2one(
        'calendar.event',
        string='Next Event',
        compute='_compute_next_event',
    )
    next_event_date = fields.Char(
        string='Next Event Date',
        compute='_compute_next_event',
    )

    def action_schedule_meeting(self):
        """Takvim’de yeni bir etkinlik (meeting) açmak için calendar.action_calendar_event action'ını döner."""
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').read()[0]

        demo_cat = self.env['calendar.event.type'].search(
            [('name', 'ilike', 'demo')], limit=1
        )
        default_cats = [(6, 0, [demo_cat.id])] if demo_cat else []
        ctx = dict(self.env.context or {},
                   default_res_model='project.project',
                   default_res_id=self.id,
                   default_name=self.name,
                   default_start=fields.Datetime.now(),
                   default_categ_ids=default_cats,
                   )
        action.update({
            'context': ctx,
            'domain': [('res_model', '=', 'project.project'), ('res_id', '=', self.id)],
        })
        return action

    @api.depends('event_ids.start')
    def _compute_next_event(self):
        now = fields.Datetime.now()
        for rec in self:
            # Gelecekteki etkinlikleri filtrele ve sıralı al
            future = rec.event_ids.filtered(lambda e: e.start and e.start >= now)
            future = future.sorted(key='start')
            if future:
                rec.next_event_id = future[0]
                rec.next_event_date = fields.Datetime.to_string(future[0].start)
            else:
                rec.next_event_id = False
                rec.next_event_date = False

    def action_view_next_event(self):
        """Tıklanınca takvimi o etkinliğe odaklayarak açar."""
        self.ensure_one()
        if not self.next_event_id:
            return {'type': 'ir.actions.act_window_close'}
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        action.update({
            'view_mode': 'calendar,form',
            'domain': [('id', '=', self.next_event_id.id)],
            'context': dict(self.env.context or {},
                            default_res_model='project.project',
                            default_res_id=self.id,
                            ),
        })
        return action
