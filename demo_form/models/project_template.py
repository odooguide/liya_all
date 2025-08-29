from odoo import fields, models, _, api
from odoo.exceptions import UserError,AccessError
from datetime import datetime,date
from odoo.osv.expression import OR, AND

def _as_date(val):
    """val -> datetime.date | None. dd.mm.yyyy / yyyy-mm-dd vb. formatları destekler."""
    if not val:
        return None
    if isinstance(val, date):
        return val
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str):
        s = val.strip()
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                pass
    return None


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
        compute='_compute_so_people_count',
        store=True,
        readonly=True,
        compute_sudo=True,
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
    event_date=fields.Date(string='Event Date',compute='_compute_crm_sale_fields',compute_sudo=True)

    related_sale_order_ids = fields.Many2many(
        comodel_name='sale.order',
        relation='project_sale_order_rel',
        column1='project_id',
        column2='sale_order_id',
        string='Bağlı Satışlar',
        compute='_compute_related_sale_orders',
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        'related_sale_order_ids.order_line.product_uom',
        'related_sale_order_ids.order_line.product_uom_qty',
    )
    def _compute_so_people_count(self):
        # UoM'i 'Kişi/kisi/people' olanları bul
        kisi_uoms = self.env['uom.uom'].search([
            '|', '|',
            ('name', 'ilike', 'kişi'),
            ('name', 'ilike', 'kisi'),
            ('name', 'ilike', 'people'),
        ])
        kisi_uom_ids = kisi_uoms.ids

        for project in self:
            if not project.related_sale_order_ids or not kisi_uom_ids:
                project.so_people_count = 0
                continue

            lines = self.env['sale.order.line'].search([
                ('order_id', 'in', project.related_sale_order_ids.ids),
                ('product_uom', 'in', kisi_uom_ids),
                ('display_type', '=', False),  # section/note hariç
            ])
            project.so_people_count = int(sum(lines.mapped('product_uom_qty')))

    @api.depends('reinvoiced_sale_order_id')
    def _compute_related_sale_orders(self):
        SaleOrder = self.env['sale.order']
        for rec in self:
            so = rec.reinvoiced_sale_order_id
            if not so:
                rec.related_sale_order_ids = [(5, 0, 0)]
                continue

            domains = []
            if so.opportunity_id:
                domains.append([('opportunity_id', '=', so.opportunity_id.id)])

            commercial = so.partner_id.commercial_partner_id if so.partner_id else False
            if commercial:
                domains.append([('partner_id', 'child_of', commercial.id)])

            if domains:
                domain = AND([OR(domains), [('state', 'in', ['done','sale'])]])
            else:
                domain = [('id', '=', so.id)]

            orders = SaleOrder.search(domain)
            rec.related_sale_order_ids = [(6, 0, orders.ids)]
            
    def _check_project_rights(self):
        self.ensure_one()
        user = self.env.user
        is_org_manager = user.has_group('__export__.res_groups_102_8eb2392b')
        is_admin = user.has_group('base.group_system')

        if is_admin or is_org_manager or self.user_id.id == user.id:
            return True

        raise UserError(_("Bu işlemi yalnızca Proje Yöneticisi, Organizasyon Müdürü "
                          "veya 'Demo Randevu Oluşturma' görevinin atanan kullanıcısı yapabilir."))


    @api.depends(
        'reinvoiced_sale_order_id',
        'reinvoiced_sale_order_id.opportunity_id',
        'reinvoiced_sale_order_id.opportunity_id.partner_id',
        'reinvoiced_sale_order_id.opportunity_id.second_contact',
        'reinvoiced_sale_order_id.opportunity_id.request_date',
        'reinvoiced_sale_order_id.opportunity_id.yabanci_turk',
        'reinvoiced_sale_order_id.people_count',
        'reinvoiced_sale_order_id.sale_order_template_id',
        'reinvoiced_sale_order_id.coordinator_ids',
        'reinvoiced_sale_order_id.wedding_date'
    )
    def _compute_crm_sale_fields(self):
        for rec in self:
            rec.crm_partner_id = False
            rec.crm_second_contact = False
            rec.crm_request_date = False
            rec.crm_yabanci_turk = False
            rec.so_sale_template_id = False
            rec.so_coordinator_ids = [(6, 0, [])]
            rec.so_opportunity_id = False
            rec.event_date = False

            so = rec.reinvoiced_sale_order_id
            if not so:
                continue

            opp = so.opportunity_id

            rec.so_sale_template_id = so.sale_order_template_id.id or False
            rec.so_coordinator_ids = [(6, 0, so.coordinator_ids.ids)] if so.coordinator_ids else [(6, 0, [])]
            rec.so_opportunity_id = opp or False  # many2one'a recordset vermek OK
            rec.event_date = so.wedding_date or False

            if opp:
                rec.crm_partner_id = opp.partner_id.id if opp.partner_id else False
                rec.crm_second_contact = opp.second_contact or False
                rec.crm_request_date = opp.request_date or False
                rec.crm_yabanci_turk = opp.yabanci_turk.id if opp.yabanci_turk else False


    @api.depends('event_ids.start', 'demo_form_ids.confirmed_demo_form_plan')
    def _compute_demo_state(self):
        for rec in self:
            # Demo tarihi var mı? (herhangi bir etkinlikte start varsa yeter)
            has_demo_date = bool(rec.event_ids.filtered('start'))

            # Onaylı demo form var mı?
            confirmed_any = any(rec.demo_form_ids.mapped('confirmed_demo_form_plan'))

            next_date = _as_date(rec.next_event_date)
            if next_date and next_date < fields.Date.today() and confirmed_any:
                rec.demo_state = 'completed'
            elif has_demo_date:
                rec.demo_state = 'planned'
            else:
                rec.demo_state = 'no_date'

    def _is_discount_line(self, line):
        name = (line.name or '').lower()
        if line.price_unit and line.price_unit < 0:
            return True
        if 'discount' in name or 'indirim' in name:
            return True
        return False

    @api.depends('reinvoiced_sale_order_id')  # sadece header bazı alanlar için gerekli
    def _compute_sale_order_summary(self):
        for rec in self:
            so = rec.reinvoiced_sale_order_id
            if not so:
                rec.sale_order_summary = False
                continue

            opportunity = so.opportunity_id
            coordinators = ', '.join(
                so.coordinator_ids.mapped('display_name')) if 'coordinator_ids' in so._fields else ''

            summary_pairs = [
                ('Müşteri', (opportunity.name if opportunity else '') or ''),
                ('Koordinatör', coordinators or ''),
                ('Satış Temsilcisi', so.user_id.display_name or ''),
                ('Kişi Sayısı', so.people_count or ''),
                ('Sözleşme Tarihi', so.contract_date or ''),
                ('Demo Tarihi', rec.next_event_date or ''),
                ('Birincil Kontak',
                 (opportunity.partner_id.name if opportunity and opportunity.partner_id else '') or ''),
                ('Birincil Mail', (opportunity.email_from if opportunity else '') or ''),
                ('Birincil Telefon', (opportunity.phone if opportunity else '') or ''),
                ('Birincil Meslek', (opportunity.function if opportunity else '') or ''),
                ('İkincil Kontak', (opportunity.second_contact if opportunity else '') or ''),
                ('İkincil Mail', (opportunity.second_mail if opportunity else '') or ''),
                ('İkincil Telefon', (opportunity.second_phone if opportunity else '') or ''),
                ('İkincil Meslek', (opportunity.second_job_position if opportunity else '') or ''),
                ('İkincil Ülke',
                 (opportunity.second_country.name if opportunity and opportunity.second_country else '') or ''),
                ('Yabancı/Türk',
                 (opportunity.yabanci_turk.name if opportunity and opportunity.yabanci_turk else '') or ''),
                ('Kaynak', (opportunity.source_id.name if opportunity and opportunity.source_id else '') or ''),
                ('Kaynak Kategorisi',
                 (opportunity.wedding_place.name if opportunity and opportunity.wedding_place else '') or ''),
                ('Satış Notları', so.note or ''),
            ]

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

            orders = rec.related_sale_order_ids.exists()
            lines = orders.mapped('order_line').exists()
            lines = lines.filtered(lambda l: not rec._is_discount_line(l))
            lines = lines.sorted(key=lambda l: (l.order_id.id, l.sequence or 0))

            html += """
            <table style="width:100%; border-collapse:collapse;">
              <thead>
                <tr>
                  <th style="border:1px solid #ccc;padding:4px;">Ürün</th>
                  <th style="border:1px solid #ccc;padding:4px;">Adet</th>
                  <th style="border:1px solid #ccc;padding:4px;">Birim</th>
                </tr>
              </thead>
              <tbody>
            """
            for l in lines:
                prod = l.product_id.display_name or ''
                qty = l.product_uom_qty or 0
                uom = l.product_uom.display_name or ''
                html += f"""
                <tr>
                  <td style="border:1px solid #ccc;padding:4px;">{prod}</td>
                  <td style="border:1px solid #ccc;padding:4px;text-align:center;">{qty}</td>
                  <td style="border:1px solid #ccc;padding:4px;">{uom}</td>
                </tr>
                """
            html += "</tbody></table>"

            rec.sale_order_summary = html
            rec.som = html

    def _get_demo_task(self):
        self.ensure_one()
        Task = self.env['project.task']
        demo_task = Task.search([
            ('project_id', '=', self.id),
            ('name', 'ilike', 'Demo Randevu Oluşturma'),
        ], limit=1)
        return demo_task

    
    def action_schedule_meeting(self):
        self.ensure_one()
        if 'duygu' not in (self.env.user.name or '').lower():
            self._check_project_rights()

        action = self.env.ref('calendar.action_calendar_event').sudo().read()[0]

        demo_cat = self.env['calendar.event.type'].sudo().search([('name', 'ilike', 'demo')], limit=1)

        ctx = dict(
            self.env.context,
            default_res_model='project.project',
            default_res_id=self.id,
            default_name=self.name,
            default_start=fields.Datetime.now(),
            default_categ_ids=[(6, 0, demo_cat.ids)] if demo_cat else False,
            search_default_mymeetings=1,
        )

        cal_view = self.env.ref('calendar.view_calendar_event_calendar', raise_if_not_found=False)
        views = action.get('views') or []
        if cal_view:
            views = [(cal_view.id, 'calendar')] + [(vid, vtype) for vid, vtype in views if vtype != 'calendar']

        action.update({
            'name': _('Meetings – %s') % self.name,
            'view_mode': 'calendar,tree,form',
            'views': views or [('calendar.view_calendar_event_calendar', 'calendar')],
            'context': ctx,
            'domain': [('res_model', '=', 'project.project'), ('res_id', '=', self.id)],
            'target': 'current',
        })
        return action

    @api.depends('event_ids.start')
    def _compute_next_event(self):
        now = fields.Datetime.now()
        for rec in self:
            events = rec.event_ids.filtered(lambda e: e.start).sorted(key='start')
            if not events:
                rec.next_event_id = False
                rec.next_event_date = False
                continue

            future = [e for e in events if e.start >= now]
            chosen = future[0] if future else events[-1]

            rec.next_event_id = chosen

            dt_local = fields.Datetime.context_timestamp(rec, chosen.start)
            rec.next_event_date = dt_local.strftime('%d.%m.%Y')

    def action_view_next_event(self):
        self.ensure_one()
        if not self.next_event_id:
            return {'type': 'ir.actions.act_window_close'}

        return {
            'type': 'ir.actions.act_window',
            'name': 'Calendar',
            'res_model': 'calendar.event',
            'view_mode': 'calendar,form',
            'domain': [('id', '=', self.next_event_id.id)],
            'context': dict(self.env.context or {},
                            default_res_model='project.project',
                            default_res_id=self.id),
            'target': 'current',
        }

    @api.depends('demo_form_ids')
    def _compute_demo_form_count(self):
        for proj in self:
            proj.demo_form_count = len(proj.demo_form_ids)

    def action_open_demo_form(self):
        """Show the existing Demo Form."""
        self.ensure_one()
        if not self.demo_form_ids:
            return {'type': 'ir.actions.act_window_close'}

        demo = self.demo_form_ids[:1].sudo()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.demo.form',
            'view_mode': 'form',
            'res_id': demo.id,
            'target': 'current',
        }

    def action_create_demo_form(self):
        """Create a new Demo Form with pre-filled values and open it."""
        self.ensure_one()
        self._check_project_rights()
        if self.demo_form_ids:
            return self.action_open_demo_form()

        vals = {
            'project_id': self.id,
        }

        order = self.sudo().reinvoiced_sale_order_id
        if order:
            # --- Güvenli davetiye adı ---
            partner = (order.partner_id.name or '').strip()
            second = (getattr(order.opportunity_id, 'second_contact', '') or '').strip()
            inv_name = f'{partner}-{second}'.strip('-').strip()

            vals.update({
                'name': f'{inv_name} Demo Formu' if inv_name else 'Demo Formu',
                'invitation_owner': inv_name or partner or False,
                'invitation_date': order.wedding_date,  # Date obj veya 'YYYY-MM-DD'
                'guest_count': order.people_count,
                'sale_template_id': order.sale_order_template_id.id or False,
                'demo_date': (
                        self.next_event_date
                        and datetime.strptime(self.next_event_date, "%d.%m.%Y").date().isoformat()
                        or False
                ),
            })

            sched_cmds = [
                (0, 0, {
                    'sequence': line.sequence,
                    'event': line.event,
                    'time': line.time,
                    'location_type': line.location_type,
                    'location_notes': line.location_notes,
                })
                for line in order.sale_order_template_id.schedule_line_ids
            ]
            vals['schedule_line_ids'] = sched_cmds

            trans_cmds = [
                (0, 0, {
                    'sequence': line.sequence,
                    'label': line.label,
                    'time': line.time,
                    'port_ids': [(6, 0, line.port_ids.ids)],
                    'other_port': line.other_port,
                })
                for line in order.sale_order_template_id.transport_line_ids
            ]
            vals['transport_line_ids'] = trans_cmds

            def _apply_hair_choice(_vals):
                date_str = _vals.get('invitation_date') or _vals.get('demo_date')
                if not date_str:
                    return
                dt = fields.Date.from_string(date_str)
                # Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
                if dt.weekday() in (2, 3, 4, 5):
                    _vals['hair_studio_3435'] = True
                else:
                    _vals['hair_garage_caddebostan'] = True

            for sol in order.order_line:
                pname = (sol.product_id.name or '').strip()
                up = pname.upper()

                if pname == "Photo & Video Plus":
                    vals['photo_video_plus'] = True
                if pname == "Drone Kamera":
                    vals['photo_drone'] = True

                # HDD teslim (SELECTION!)
                if pname == "Hard Disk 1TB Delivered":
                    vals['photo_harddisk_delivered'] = 'delivered'
                if pname == "Will Deliver Later":
                    vals['photo_harddisk_delivered'] = 'later'

                # After party & alt opsiyonlar
                if pname == "After Party":
                    vals['afterparty_service'] = True
                if pname == "After Party Shot Servisi":
                    vals['afterparty_shot_service'] = True
                if pname == "Sushi Bar":
                    vals['afterparty_sushi'] = True
                if pname == "After Party Ultra":
                    vals['afterparty_ultra'] = True  # constrains/onchange kontrol edecek
                    vals['afterparty_fog_laser'] = True
                    vals['afterparty_shot_service'] = True
                if pname == "Dans Show":
                    vals['afterparty_dance_show'] = True
                if pname == "Fog + Laser Show":
                    vals['afterparty_fog_laser'] = True

                # Bar
                if pname == "Yabancı İçki Servisi":
                    vals['bar_alcohol_service'] = True

                # Saç & makyaj
                if pname == "Saç & Makyaj":
                    _apply_hair_choice(vals)

                # Müzik & pasta
                if "Canlı Müzik" in pname:
                    vals['music_live'] = True
                if "Pasta Show'da Gerçek Pasta" in pname:
                    vals['cake_real'] = True
                if "Pasta Show'da Şampanya Kulesi" in pname:
                    vals['cake_champagne_tower'] = True
                if "PERKÜSYON" in up:
                    vals['music_percussion'] = True
                if "TRIO" in up:
                    vals['music_trio'] = True
                if "Özel" in pname:
                    vals['music_other'] = True
                    vals['music_other_details'] = "Custom Live Music package"

                # DJ (project alanı varsa formla senkron)
                if self.dj_person:
                    vals['dj_person'] = self.dj_person

                # Pre-host
                if up == "BARNEY":
                    vals['prehost_barney'] = True
                if up == "FRED":
                    vals['prehost_fred'] = True
                if pname == "Breakfast Service":
                    vals['prehost_breakfast'] = True
                    vals['prehost_breakfast_count'] = int(sol.product_uom_qty or 0)

            tmpl = (order.sale_order_template_id.name or '').strip().lower()
            elite_fields = [
                'photo_video_plus',
                'afterparty_service', 'afterparty_shot_service',
                'accommodation_service', 'dance_lesson',
            ]
            ultra_extra = [
                'music_live', 'music_percussion', 'music_trio',
                'photo_yacht_shoot', 'bar_alcohol_service','afterparty_sushi',
                'photo_drone', 'afterparty_fog_laser', 'prehost_barney','afterparty_bbq_wraps'
            ]
            ultra_fields = elite_fields + ultra_extra

            vals['photo_standard'] = (tmpl == 'elite')

            if tmpl == 'plus':
                _apply_hair_choice(vals)
                for f in elite_fields:
                    vals[f] = True

            elif tmpl == 'ultra':
                _apply_hair_choice(vals)
                for f in ultra_fields:
                    vals[f] = True
                vals['afterparty_ultra'] = True
        if self.user_id == self.env.user:
            demo = self.env['project.demo.form'].sudo().create(vals)
        else:
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
            self.mapped('demo_form_ids').sudo().write({'dj_person': vals['dj_person']})
        return res

    def _get_done_stage(self):
        """stage_id'nin comodel'ini dinamik bul ve 'Tamamlanan/Done/Completed/Bitti' benzeri bir stage getir."""
        field = self._fields.get('stage_id')
        if not field or field.type != 'many2one':
            return self.env['ir.model'].browse()
        model_name = getattr(field, 'comodel_name', False)
        if not model_name:
            return self.env['ir.model'].browse()
        Stage = self.env[model_name].sudo()
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

    def action_compose_whatsapp_message(self):
        self.ensure_one()
        self._check_project_rights()
        project = self

        demo = self.env['project.demo.form'].search([('project_id', '=', project.id)], limit=1)
        if not demo:
            raise UserError(_("Bu projeye bağlı mesaj kaynağı (demo form) bulunamadı."))

        html_body = demo._build_whatsapp_message()

        ctx = {
            'default_model': 'project.project',
            'default_res_ids':[project.id],
            'default_composition_mode': 'comment',
            'default_is_log': True,
            'default_subtype_id': self.env.ref('mail.mt_note').id,
            'default_subject': 'WhatsApp Mesajı',
            'default_body': html_body,
        }

        view = self.env.ref('mail.email_compose_message_wizard_form')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Log Ekle (WhatsApp)',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'view_id': view.id,
            'target': 'new',
            'context': ctx,
        }