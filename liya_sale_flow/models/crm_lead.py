from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError, UserError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    option1 = fields.Date(string="Alternatif Tarih 1")
    option2 = fields.Date(string="Alternatif Tarih 2")
    option3 = fields.Date(string="Alternatif Tarih 3")
    wedding_type = fields.Many2one(
        comodel_name="wedding.type",
        string="Düğün Tipi",
        ondelete="set null",
    )
    request_date = fields.Date(string="Talep Tarihi")
    wedding_year = fields.Char(
        string="Düğün Yılı",
        size=4,
        help="Düğün yılı (2025-2100 arası)"
    )
    people = fields.Integer(string="Kişiler")
    second_contact = fields.Char(
        string="İkincil Kontakt",
    )
    second_phone = fields.Char(string="İkincil Telefon")
    second_mail = fields.Char(string="İkincil Mail")
    second_job_position = fields.Char(string="İkincil Meslek")
    second_title = fields.Many2one(
        comodel_name='res.partner.title',
        string='Ikincil Başlık',
        help='Kontakt kartındaki unvanlar listesinden seçiniz.'
    )

    type = fields.Selection(
        [('lead', 'Lead'), ('opportunity', 'Opportunity')],
        compute='_compute_type',
        store=True,
        readonly=False,
    )

    my_activity_date_clock = fields.Char(
        string='Aktivite Saati',
        compute='_compute_activity_date_time',
        store=True,
    )

    my_activity_date = fields.Char(
        string='Aktivite Tarihi',
        compute='_compute_activity_date_time',
        store=True,
    )

    my_activity_day = fields.Char(
        string='Gun',
        compute='_compute_activity_day',
        store=True,
    )
    wedding_place=fields.Many2one('wedding.place',string='Kaynak Kategori',ondelete="set null")


    @api.constrains('wedding_year')
    def _check_wedding_year(self):
        if self.wedding_year:
            if not self.wedding_year.isdigit():
                raise ValidationError("Düğün yılı sadece sayı içermelidir.")

            if len(self.wedding_year) != 4:
                raise ValidationError("Düğün yılı 4 haneli olmalıdır.")

            year = int(self.wedding_year)

            if year < 2024:
                raise ValidationError("Düğün yılı 2024'den büyük olmalıdır (minimum 2025).")

            if year > 2100:
                raise ValidationError("Düğün yılı 2100'den küçük olmalıdır (maksimum 2100).")

    def action_set_lost(self, **additional_values):
        res = super().action_set_lost(**additional_values)
        # ilgili tüm sale.order kayıtlarını al
        orders = self.env['sale.order'].search([
            ('opportunity_id', 'in', self.ids),
        ])
        for order in orders:
            order._action_cancel()
        return res

    @api.depends('activity_type_id')
    def _compute_type(self):
        for lead in self:
            display = lead.activity_type_id and lead.activity_type_id.display_name or ''
            if 'Toplantı' in display:
                lead.type = 'opportunity'

        return None

    @api.depends('my_activity_date')
    def _compute_activity_day(self):
        turkish_days = [
            'Pazartesi', 'Salı', 'Çarşamba',
            'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'
        ]
        for rec in self:
            if rec.my_activity_date:
                try:
                    date_obj = datetime.strptime(rec.my_activity_date, '%d.%m.%Y').date()
                    rec.my_activity_day = turkish_days[date_obj.weekday()]
                except ValueError:
                    rec.my_activity_day = False
            else:
                rec.my_activity_day = False

    @api.depends('calendar_event_ids.start')
    def _compute_activity_date_time(self):
        for lead in self:
            if not lead.calendar_event_ids:
                lead.my_activity_date_clock = False
                continue

            event = lead.calendar_event_ids[0]
            start_dt = event.start
            if isinstance(start_dt, str):
                start_dt = fields.Datetime.from_string(start_dt)
            dt_with_offset = start_dt + timedelta(hours=3)
            lead.my_activity_date_clock = dt_with_offset.strftime('%H:%M')
            lead.my_activity_date = start_dt.strftime('%d.%m.%Y')

    @api.model
    def _get_first_stage(self, team):
        return self.env['crm.stage'].search([
            ('team_id', '=', team.id),
            ('sequence', '=', 1)], limit=1)

    def write(self, vals):
        if 'stage_id' not in vals:
            return super().write(vals)

        for lead in self:
            old_seq = lead.stage_id.sequence
            new_stage = self.env['crm.stage'].browse(vals['stage_id'])
            new_seq = new_stage.sequence

            if new_seq <= old_seq:
                continue

            if new_stage.name == 'Görüşülüyor / Teklif Süreci':
                if lead.quotation_count < 1:
                    raise UserError(_('Teklif oluşturmadan "Teklif Süreci"ne geçemezsiniz.'))


            elif new_stage.name == 'Sözleşme Süreci':
                orders = self.env['sale.order'].search([
                    ('opportunity_id', '=', lead.id),
                    ('state', 'in', ('sale', 'done'))
                ])
                if not orders:
                    raise UserError(
                        _('Onaylı teklif yok, "Sözleşme Süreci"ne geçemezsiniz.')
                    )
            if new_stage.name == 'Kazanıldı':
                orders = self.env['sale.order'].search([
                    ('opportunity_id', '=', lead.id),
                    ('state', 'in', ('sale', 'done'))
                ])

                has_confirmed = any(order.confirmed_contract for order in orders)
                if not has_confirmed:
                    raise UserError(
                        _('Hiçbir onaylı sözleşme bulunamadı. "Kazanıldı" aşamasına geçemezsiniz.')
                    )

                order = orders[0]

                wedding_tag = self.env['calendar.event.type'].search(
                    [('name', '=', 'Düğün')], limit=1
                )
                all_partner_ids = order.coordinator_ids.ids

                partner_ops = [(4, pid) for pid in all_partner_ids]

                self.env['calendar.event'].create({
                    'name': f'{lead.name} Düğün Günü',
                    'start_date': order.wedding_date,
                    'stop_date': order.wedding_date,
                    'allday': True,
                    'user_id': lead.user_id.id,
                    'partner_ids': partner_ops,
                    'categ_ids': [(6, 0, [wedding_tag.id])] if wedding_tag else [],
                    'opportunity_id': self.id,
                })

                orders_to_cancel=self.env['sale.order'].search([
                    ('opportunity_id', '=', lead.id),
                    ('state', 'in', ('draft','sent'))
                ])

                for o in orders_to_cancel:
                    o._action_cancel()


        return super().write(vals)

    def action_sale_quotations_new(self):
        self.ensure_one()
        action = super(CrmLead, self).action_sale_quotations_new()
        ctx = dict(action.get('context', {}))
        ctx.update({
            'default_second_contact': self.second_contact or False,
            'default_wedding_date': self.option1 or False,
        })
        action['context'] = ctx
        return action

    @api.onchange('source_id')
    def _onchange_source(self):
        if self.source_id and self.source_id.name == 'Düğün.com':
            rec = self.env['wedding.place'].search(
                [('name', '=', 'Kır Düğünü')],
                limit=1
            )
            if rec:
                self.wedding_place = rec.id




#TODO: partner_ids coordinatorler, sales person user_id tum gun