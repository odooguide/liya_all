from odoo import fields, models, _, api
from odoo.exceptions import UserError


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

    seat_plan = fields.Binary(string="Seat Plan")
    seat_plan_name = fields.Char(string="Seat Plan Name")
    sale_order_summary = fields.Html(
        string="Sale Order Summary",
        compute='_compute_sale_order_summary',
        compute_sudo=True,
        sanitize=False,
        readonly=True,
        help="Sale Order'dan (indirim satırları hariç) çekilen özet bilgi."
    )
    som = fields.Html(
        string="Sale Order Summary",
        sanitize=False,
        readonly=True,
        help="Sale Order'dan (indirim satırları hariç) çekilen özet bilgi."
    )
    dj_person=fields.Selection([('engin','DJ: Engin Sadiki'),('fatih','DJ: Fatih Aşçı'),('other','Diğer')], string='DJ')
    crm_partner_id = fields.Many2one(
        'res.partner',
        string='Müşteri',
        compute='_compute_crm_sale_fields',
        store=True,
        readonly=True
    )
    crm_second_contact = fields.Char(
        string='İkincil Kontak',
        compute='_compute_crm_sale_fields',
        store=True,
        readonly=True
    )
    crm_request_date = fields.Date(
        string='Talep Tarihi',
        compute='_compute_crm_sale_fields',
        store=True,
        readonly=True
    )
    crm_yabanci_turk = fields.Many2one(
        'foreign.local',
        string='Yabancı/Türk',
        compute='_compute_crm_sale_fields',
        store=True,
        readonly=True
    )

    so_people_count = fields.Integer(
        string='Kişi Sayısı',
        compute='_compute_crm_sale_fields',
        store=True,
        readonly=True
    )
    so_sale_template_id = fields.Many2one(
        'sale.order.template',
        string='Satış Şablonu',
        compute='_compute_crm_sale_fields',
        store=True,
        readonly=True
    )
    so_coordinator_ids = fields.Many2many(
        'res.partner',
        string='Koordinatörler',
        compute='_compute_crm_sale_fields',
        store=True,
        readonly=True
    )
    demo_state = fields.Selection([
        ('no_date', 'Demo Tarihi Atanmamış'),
        ('completed', 'Demo Tamamlandı'),
        ('planned', 'Demo Planlandı'),
    ], string='Demo Durumu', compute='_compute_demo_state', store=True)
    so_opportunity_id=fields.Many2one(
        'crm.lead',
        string='Fırsat',
        compute='_compute_crm_sale_fields',
        store=True,
        readonly=True)

    @api.depends('reinvoiced_sale_order_id',
                 'reinvoiced_sale_order_id.opportunity_id',
                 'reinvoiced_sale_order_id.opportunity_id.partner_id',
                 'reinvoiced_sale_order_id.opportunity_id.second_contact',
                 'reinvoiced_sale_order_id.opportunity_id.request_date',
                 'reinvoiced_sale_order_id.opportunity_id.yabanci_turk',
                 'reinvoiced_sale_order_id.people_count',
                 'reinvoiced_sale_order_id.sale_order_template_id',
                 'reinvoiced_sale_order_id.coordinator_ids',
                 'reinvoiced_sale_order_id.opportunity_id')
    def _compute_crm_sale_fields(self):
        for rec in self:
            so = rec.reinvoiced_sale_order_id
            if so:
                opp = so.opportunity_id
                rec.crm_partner_id = opp.partner_id.id or False
                rec.crm_second_contact = opp.second_contact or False
                rec.crm_request_date = opp.request_date or False
                rec.crm_yabanci_turk = opp.yabanci_turk.id or False
                rec.so_people_count = so.people_count or 0
                rec.so_sale_template_id = so.sale_order_template_id.id or False
                rec.so_coordinator_ids = [(6, 0, so.coordinator_ids.ids)]
                rec.so_opportunity_id=opp
            else:
                rec.crm_partner_id = False
                rec.crm_second_contact = False
                rec.crm_request_date = False
                rec.crm_yabanci_turk = False
                rec.so_people_count = 0
                rec.so_sale_template_id = False
                rec.so_coordinator_ids  = [(5, 0, 0)]
                rec.so_opportunity_id=False,


    @api.depends('event_ids.start')
    def _compute_demo_state(self):
        today = fields.Date.today()
        for rec in self:
            dates = rec.event_ids.mapped('start')
            if not dates:
                rec.demo_state = 'no_date'
            else:
                earliest = min(dates)
                dt_obj = fields.Datetime.from_string(earliest)
                date_val = dt_obj.date() if dt_obj else None
                if self.demo_form_ids:
                    for demo in self.demo_form_ids:
                        if date_val and demo.confirmed_demo_form_plan:
                            rec.demo_state = 'completed'
                        else:
                            rec.demo_state = 'planned'

    def _is_discount_line(self, line):
        name = (line.name or '').lower()
        if line.price_unit and line.price_unit < 0:
            return True
        if 'discount' in name or 'indirim' in name:
            return True
        return False

    @api.depends('reinvoiced_sale_order_id')
    def _compute_sale_order_summary(self):
        for rec in self:
            so = rec.reinvoiced_sale_order_id
            if not so:
                rec.sale_order_summary = False
                continue
            opportunity = so.opportunity_id

            summary_pairs = [
                ('Müşteri', opportunity.name or ''),
                ('Koordinator', so.coordinator_ids.display_name or ''),
                ('Satış Temsilcisi', so.user_id.display_name or ''),
                ('Kişi Sayısı', so.people_count or ''),
                ('Sözleşme Tarihi', so.contract_date or ''),
                ('Demo Tarihi', self.next_event_date or ''),
                ('Birincil Kontak', opportunity.partner_id.name or ''),
                ('Birincil Mail', opportunity.email_from or ''),
                ('Birincil Telefon', opportunity.phone or ''),
                ('Birincil Meslek', opportunity.function or ''),
                ('İkincil Kontak', opportunity.second_contact or ''),
                ('İkincil Mail', opportunity.second_mail or ''),
                ('İkincil Telefon', opportunity.second_phone or ''),
                ('İkincil Meslek', opportunity.second_job_position or ''),
                ('İkincil Ülke', opportunity.second_country.name or ''),
                ('Yabancı/Türk', opportunity.yabanci_turk.name or ''),
                ('Kaynak', opportunity.source_id.name or ''),
                ('Kaynak Kategorisi', opportunity.wedding_place.name or ''),
            ]

            # Başlangıçta tabloyu açıyoruz
            html = """
            <table style="width:100%; border-collapse:collapse; margin-bottom:10px;">
              <tbody>
            """
            for i in range(0, len(summary_pairs), 2):
                key1, val1 = summary_pairs[i]
                if i + 1 < len(summary_pairs):
                    key2, val2 = summary_pairs[i + 1]
                else:
                    key2, val2 = '', ''
                html += f"""
                <tr>
                  <td style="padding:4px; vertical-align:top;">
                    <strong>{key1}:</strong> {val1}
                  </td>
                  <td style="padding:4px; vertical-align:top;">
                    {'<strong>%s:</strong> %s' % (key2, val2) if key2 else ''}
                  </td>
                </tr>
                """
            html += """
              </tbody>
            </table>
            <hr style="margin:10px 0;"/>
            """

            lines = so.order_line.filtered(lambda l: not rec._is_discount_line(l))
            html += """
            <table style="width:100%; border-collapse:collapse;">
              <thead>
                <tr>
                  <th style="border:1px solid #ccc;padding:4px;">Ürün</th>
                  <th style="border:1px solid #ccc;padding:4px;">Açıklama</th>
                  <th style="border:1px solid #ccc;padding:4px;">Adet</th>
                  <th style="border:1px solid #ccc;padding:4px;">Birim</th>
                </tr>
              </thead>
              <tbody>
            """
            for l in lines:
                prod = l.product_id.display_name or ''
                desc = l.name if l.name != prod else ''
                qty = l.product_uom_qty or 0
                uom = l.product_uom.display_name or ''
                html += f"""
                <tr>
                  <td style="border:1px solid #ccc;padding:4px;">{prod}</td>
                  <td style="border:1px solid #ccc;padding:4px;">{desc}</td>
                  <td style="border:1px solid #ccc;padding:4px;text-align:center;">{qty}</td>
                  <td style="border:1px solid #ccc;padding:4px;">{uom}</td>
                </tr>
                """
            html += "</tbody></table>"

            rec.sale_order_summary = html
            rec.som=html

    @api.onchange('confirmed_demo_form_plan')
    def _onchange_confirmed_contract_security(self):
        for rec in self:
            origin = rec._origin
            if origin.confirmed_demo_form_plan and not self.env.user.has_group('base.group_system'):
                rec.seat_plan = origin.seat_plan
                raise UserError(
                    _('Only administrators can modify or delete the Confirmed Demo Form once uploaded.')
                )

    def _get_demo_task(self):
        self.ensure_one()
        Task = self.env['project.task']
        demo_task = Task.search([
            ('project_id', '=', self.id),
            ('name', 'ilike', 'Demo Randevu Oluşturma'),
        ], limit=1)
        return demo_task

    def _check_schedule_demo_rights(self):
        self.ensure_one()
        user = self.env.user

        is_project_manager = user.has_group('__export__.res_groups_101_9be46a0ar')
        is_org_manager = user.has_group('__export__.res_groups_102_8eb2392b')
        is_admin = user.has_group('base.group_system')

        if is_admin or is_project_manager or is_org_manager or self.user_id.id == user.id:
            return True

        demo_task = self._get_demo_task()
        if demo_task and (user in demo_task.user_ids or getattr(demo_task, 'user_id', False) == user):
            return True

        raise UserError(_("Bu işlemi yalnızca Proje Yöneticisi, Organizasyon Müdürü "
                          "veya 'Demo Randevu Oluşturma' görevinin atanan kullanıcısı yapabilir."))

    def action_schedule_meeting(self):
        self.ensure_one()
        self._check_schedule_demo_rights()

        action = self.env.ref('calendar.action_calendar_event').sudo().read()[0]
        demo_cat = self.env['calendar.event.type'].sudo().search([('name', 'ilike', 'demo')], limit=1)
        default_cats = [(6, 0, [demo_cat.id])] if demo_cat else []

        ctx = dict(
            self.env.context,
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
            inv_name = f'{order.partner_id.name}-{order.opportunity_id.second_contact}'
            vals.update({
                'name': f'{inv_name} Demo Formu',
                'invitation_owner': inv_name,
                'invitation_date': order.wedding_date,
                'guest_count': order.people_count,
                'sale_template_id': order.sale_order_template_id.id or False,
                'demo_date': self.next_event_date
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
                if name == "Photo & Video Plus":
                    vals['photo_video_plus'] = True
                if name == "Drone Kamera":
                    vals['photo_drone'] = True

                if name == "Hard Disk 1TB Delivered":
                    vals['photo_harddisk_delivered'] = True
                if name == "Will Deliver Later":
                    vals['photo_harddisk_later'] = True

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
                if name == "After Party Ultra":
                    vals['afterparty_ultra'] = True

                if name == "Saç & Makyaj":
                    date_str = vals.get('invitation_date') or vals.get('demo_date')
                    if date_str:
                        dt = fields.Date.from_string(date_str)
                        # Monday=0, Tuesday=1, Wednesday=2
                        if dt.weekday() in (2, 3, 4, 5):
                            vals['hair_studio_3435'] = True
                        else:
                            vals['hair_garage_caddebostan'] = True

                if "Canlı Müzik" in name:
                    vals['music_live'] = True
                if "Pasta Show'da Gerçek Pasta" in name:
                    vals['cake_real'] = True
                if "Pasta Show'da Şampanya Kulesi" in name:
                    vals['cake_champagne_tower'] = True
                if "PERKÜSYON" in name.upper():
                    vals['music_percussion'] = True
                if "TRIO" in name.upper():
                    vals['music_trio'] = True
                if "Özel" in name:
                    vals['music_other'] = True
                    vals['music_other_details'] = "Custom Live Music package"
                if self.dj_person:
                    vals['dj_person']=self.dj_person
                if name.upper() == "BARNEY":
                    vals['prehost_barney'] = True
                if name.upper() == "FRED":
                    vals['prehost_fred'] = True


                if name == "Breakfast Service":
                    vals['prehost_breakfast'] = True
                    vals['prehost_breakfast_count'] = int(sol.product_uom_qty)
                vals['photo_standard'] = True

                # if name == "Pasta Show'da Gerçek Pasta":
                #     vals['cake_choice'] = 'real'
                # if name == "Pasta Show'da Şampanya Kulesi":
                #     vals['cake_choice'] = 'champagne'

            tmpl = (order.sale_order_template_id.name or '').strip().lower()
            elite_fields = [
                'photo_video_plus',
                'afterparty_service', 'afterparty_shot_service',
                'afterparty_sushi',
                 'afterparty_fog_laser',
                'accommodation_service','dance_lesson',
            ]

            ultra_extra = ['music_live', 'music_percussion', 'music_trio','photo_yacht_shoot','table_fresh_flowers','bar_alcohol_service',
                           'photo_drone',]
            ultra_fields = elite_fields + ultra_extra
            if tmpl == 'plus':
                date_str = vals.get('invitation_date') or vals.get('demo_date')
                if date_str:
                    dt = fields.Date.from_string(date_str)
                    # Monday=0, Tuesday=1, Wednesday=2
                    if dt.weekday() in (2, 3, 4, 5):
                        vals['hair_studio_3435'] = True
                    else:
                        vals['hair_garage_caddebostan'] = True

                for f in elite_fields:
                    vals[f] = True
                if name == 'After Party Ultra':
                    vals['afterparty_ultra'] = True
                vals['start_end_time'] = '19:30 - 1:30'

            elif tmpl == 'ultra':
                date_str = vals.get('invitation_date') or vals.get('demo_date')
                if date_str:
                    dt = fields.Date.from_string(date_str)
                    # Monday=0, Tuesday=1, Wednesday=2
                    if dt.weekday() in (2, 3, 4, 5):
                        vals['hair_studio_3435'] = True
                    else:
                        vals['hair_garage_caddebostan'] = True
                for f in ultra_fields:
                    vals[f] = True
                vals['afterparty_ultra'] = True
                vals['start_end_time'] = '19:30 - 2:00'
            else:
                vals['start_end_time'] = '19:30 - 23:30'

        demo = self.env['project.demo.form'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.demo.form',
            'view_mode': 'form',
            'res_id': demo.id,
            'target': 'current',
        }

    def write(self, vals):
        res = super().write(vals)
        if 'dj_person' in vals:
            self.mapped('demo_form_ids').write({'dj_person': vals['dj_person']})
        return res

    def _get_done_stage(self):
        """stage_id'nin comodel'ini dinamik bul ve 'Tamamlanan/Done/Completed/Bitti' benzeri bir stage getir."""
        field = self._fields.get('stage_id')
        if not field or field.type != 'many2one':
            return self.env['ir.model'].browse()  # boş recordset

        model_name = getattr(field, 'comodel_name', False)
        if not model_name:
            return self.env['ir.model'].browse()

        Stage = self.env[model_name].sudo()

        # Önce isimden bulmaya çalış
        stage = Stage.search([
            '|', '|', '|', '|',
            ('name', '=', 'Tamamlanan'),
            ('name', '=', 'Completed'),
            ('name', '=', 'Bitti'),
            ('name', '=', 'Done'),
            ('name', 'ilike', 'Complet'),
        ], limit=1)

        if stage:
            return stage

        if 'is_closed' in Stage._fields:
            stage = Stage.search([('is_closed', '=', True)], limit=1)
            if stage:
                return stage

        if 'fold' in Stage._fields:
            stage = Stage.search([('fold', '=', True)], limit=1)
            if stage:
                return stage

        return self.env[model_name].browse()

    @api.model
    def cron_update_stage_by_wedding_date(self):
        today = fields.Date.context_today(self)
        records = self.search([
            ('reinvoiced_sale_order_id.wedding_date', '<', today),
        ])
        if not records:
            return
        done_stage = records[:1]._get_done_stage()
        if not done_stage:
            return
        for rec in records.filtered(lambda r: r.stage_id != done_stage):
            rec.stage_id = done_stage.id

