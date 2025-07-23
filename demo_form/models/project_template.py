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
    demo_form_ids = fields.One2many(
        'project.demo.form', 'project_id', string="Demo Forms")
    demo_form_count = fields.Integer(
        string="Demo Form Count", compute='_compute_demo_form_count')


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


    @api.depends('demo_form_ids')
    def _compute_demo_form_count(self):
        for proj in self:
            proj.demo_form_count = len(proj.demo_form_ids)

    def action_open_demo_form(self):
        """Show the existing Demo Form."""
        self.ensure_one()
        if not self.demo_form_ids:
            return {'type': 'ir.actions.act_window_close'}
        demo = self.demo_form_ids[0]
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.demo.form',
            'view_mode': 'form',
            'res_id': demo.id,
            'target': 'current',
        }

    def action_create_demo_form(self):
        """Create a new Demo Form with pre‑filled values and open it."""
        self.ensure_one()
        if self.demo_form_ids:
            return self.action_open_demo_form()

        vals = {
            'project_id': self.id,
        }

        order = self.reinvoiced_sale_order_id
        if order:
            vals.update({
                'invitation_owner': order.partner_id.name,
                'invitation_date': order.wedding_date,
                'guest_count': order.people_count,
                'sale_template_id': order.sale_order_template_id.id or False,
                'demo_date':self.next_event_date
            })
            sched_cmds = []
            for line in order.sale_order_template_id.schedule_line_ids:
                sched_cmds.append((0, 0, {
                    'sequence': line.sequence,
                    'event': line.event,
                    'time': line.time,
                    'location_type': line.location_type,
                    'location_notes': line.location_notes,
                }))
            vals['schedule_line_ids'] = sched_cmds
            trans_cmds = []
            for line in order.sale_order_template_id.transport_line_ids:
                trans_cmds.append((0, 0, {
                    'sequence': line.sequence,
                    'label': line.label,
                    'time': line.time,
                    'port_ids': [(6, 0, line.port_ids.ids)],
                    'other_port': line.other_port,
                }))
            vals['transport_line_ids'] = trans_cmds

            for sol in order.order_line:
                name = sol.product_id.name.strip()

                # Photography
                if name == "Photo & Video Plus":
                    vals['photo_video_plus'] = True
                if name == "Drone Kamera":
                    vals['photo_drone'] = True
                if name == "Photo Print Service":
                    vals['photo_print_service'] = True
                if name in ("Hard Disk 1 TB Delivered", "Will Deliver Later"):
                    # choose the correct key in your model:
                    vals['photo_harddisk_delivered'] = (name == "Hard Disk 1 TB Delivered")
                    vals['photo_harddisk_later'] = (name == "Will Deliver Later")

                # After Party
                if name == "After Party":
                    vals['afterparty_service'] = True
                if name == "After Party Shot Servisi":
                    vals['afterparty_shot_service'] = True
                if name == "Sushi Bar":
                    vals['afterparty_sushi'] = True
                if name == "Yabancı İçki Servisi":
                    vals['bar_alcohol_service'] = True
                if name == "Dans Show":
                    vals['afterparty_dance_show'] = True
                if name == "Fog + Laser Show":
                    vals['afterparty_fog_laser'] = True

                # Hair & Makeup
                if name == "Saç & Makyaj":
                    # we don’t know the studio, so mark “other”
                    vals['hair_other'] = True

                # Music: any “Canlı Müzik” product
                if "Canlı Müzik" in name:
                    vals['music_live'] = True
                    if "PERKÜSYON" in name.upper():
                        vals['music_percussion'] = True
                    if "TRIO" in name.upper():
                        vals['music_trio'] = True
                    # special “Özel” product
                    if "Özel" in name:
                        vals['music_other'] = True
                        vals['music_other_details'] = "Custom Live Music package"

                # Pre‑Hosting
                if name.upper() == "BARNEY":
                    vals['prehost_barney'] = True
                if name.upper() == "FRED":
                    vals['prehost_fred'] = True
                if name == "Breakfast Service":
                    vals['prehost_breakfast'] = True
                    vals['prehost_breakfast_count'] = int(sol.product_uom_qty)

                # Table/Cake
                if name == "Pasta Show'da Gerçek Pasta":
                    vals['cake_choice'] = 'real'
                if name == "Pasta Show'da Şampanya Kulesi":
                    vals['cake_choice'] = 'champagne'

        demo = self.env['project.demo.form'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.demo.form',
            'view_mode': 'form',
            'res_id': demo.id,
            'target': 'current',
        }