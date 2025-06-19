import re

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError, UserError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    date_conversion = fields.Datetime('Conversion Date', readonly=False)

    option1 = fields.Date(string="Optional Date 1")
    option2 = fields.Date(string="Optional Date 2")
    option3 = fields.Date(string="Optional Date 3")
    wedding_type = fields.Many2one(
        comodel_name="wedding.type",
        string="Event Type",
        ondelete="set null",
    )
    request_date = fields.Date(string="Request Date")
    wedding_year = fields.Char(
        string="Event Year",
        size=4,
        help="Event Year (between 2025-2100)"
    )
    people = fields.Integer(string="People",default=False)
    second_contact = fields.Char(
        string="Secondary Contact",
    )
    second_phone = fields.Char(string="Secondary Phone")
    second_mail = fields.Char(string="Secondary E-mail")
    second_job_position = fields.Char(string="Secondary Job Position")
    second_title = fields.Many2one(
        comodel_name='res.partner.title',
        string='Secondary Title',
        help='Please choose one of the titles from Contact Titles.'
    )
    second_country = fields.Many2one(
        comodel_name='res.country',
        string='Second Country',
        help='Secondary country selection'
    )


    type = fields.Selection(
        [('lead', 'Lead'), ('opportunity', 'Opportunity')],
        compute='_compute_type',
        store=True,
        readonly=False,
    )

    my_activity_date_clock = fields.Char(
        string='Activity Hour',
        compute='_compute_activity_date_time',
        store=True,
    )

    my_activity_date = fields.Char(
        string='Activity Date',
        compute='_compute_activity_date_time',
        store=True,
    )

    my_activity_day = fields.Char(
        string='Activity Day',
        compute='_compute_activity_day',
        store=True,
    )
    wedding_place=fields.Many2one('wedding.place',string='Source Category',ondelete="set null")

    yt = fields.Selection([
        ('yt', 'YT'),
        ('y', 'Y'),
        ('t', 'T'),
    ], string='Y/T')


    request_month = fields.Char(
        string='Request Month',
        compute='_compute_month_names',
        store=True,
    )

    conversion_month = fields.Char(
        string='Conversion Month',
        compute='_compute_month_names',
        store=True,
    )

    current_month = fields.Char(
        string='Current Month',
        compute='_compute_month_names',
        store=True,
    )

    @api.depends('request_date', 'date_conversion')
    def _compute_month_names(self):
        month_names = {
            1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan',
            5: 'Mayıs', 6: 'Haziran', 7: 'Temmuz', 8: 'Ağustos',
            9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'
        }
        for rec in self:
            if rec.request_date:
                rec.request_month = month_names.get(
                    rec.request_date.month, False
                )
            else:
                rec.request_month = False

            if rec.date_conversion:
                rec.conversion_month = month_names.get(
                    rec.date_conversion.month, False
                )
            else:
                rec.conversion_month = False

            today = fields.Date.context_today(self)
            current_month_num = fields.Date.from_string(today).month
            current_month_name = month_names.get(current_month_num, False)
            rec.current_month = current_month_name

    @api.onchange('second_phone')
    def _onchange_second_phone(self):
        for partner in self:
            raw = partner.second_phone or ''

            digits = re.sub(r'\D', '', raw)
            if len(digits) == 11 and digits.startswith('0'):
                digits = digits[1:]
            if len(digits) == 10:
                m = re.match(r'(\d{3})(\d{3})(\d{2})(\d{2})$', digits)
                if m:
                    part1, part2, part3, part4 = m.groups()
                    partner.second_phone = f'+90 {part1} {part2} {part3} {part4}'
                else:
                    partner.second_phone = raw
            else:
                partner.second_phone = raw
    @api.constrains('wedding_year')
    def _check_wedding_year(self):
        if self.wedding_year:
            if not self.wedding_year.isdigit():
                raise ValidationError("Etkinlik yılı sadece sayı içermelidir.")

            if len(self.wedding_year) != 4:
                raise ValidationError("Etkinlik yılı 4 haneli olmalıdır.")

            year = int(self.wedding_year)

            if year < 2024:
                raise ValidationError("Etkinlik yılı 2024'den büyük olmalıdır (minimum 2025).")

            if year > 2100:
                raise ValidationError("Etkinlik yılı 2100'den küçük olmalıdır (maksimum 2100).")

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
            if 'toplantı' or 'meeting' in display.lower():
                lead.type = 'opportunity'
                lead.date_conversion=date.today()

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
            new_stage = self.env['crm.stage'].browse(vals['stage_id'])

            if (new_stage.name == 'Görüşülüyor / Teklif Süreci' or new_stage.name == 'In Contact / Quotation Progress'):
                missing = []
                required_fields = {
                    'people': _('People'),
                    'second_contact': _('Secondary Contact'),
                    'second_phone': _('Secondary Phone'),
                    'second_mail': _('Secondary E-mail'),
                    'second_job_position': _('Secondary Job Position'),
                    'second_title': _('Secondary Title'),
                    'second_country': _('Second Country'),
                    'yt':_('YT')
                }
                for field_name, pretty in required_fields.items():
                    val = vals.get(field_name, getattr(lead, field_name))
                    if not val:
                        missing.append(pretty)
                if missing:
                    raise UserError(_(
                        '“Görüşülüyor” aşamasına geçebilmek için şu alanlar zorunlu:\n%s'
                    ) % (', '.join(missing)))

                if lead.quotation_count < 1:
                    raise UserError(_('Teklif oluşturmadan "Teklif Süreci"ne geçemezsiniz.'))

                
            elif (new_stage.name == 'Sözleşme Süreci' or new_stage.name == 'Contracting'):


                orders = self.env['sale.order'].search([
                    ('opportunity_id', '=', lead.id),
                    ('state', 'in', ('sale', 'done'))
                ])
                if not orders:
                    raise UserError(
                        _('Onaylı teklif yok, "Sözleşme Süreci"ne geçemezsiniz.')
                    )
            if (new_stage.name == 'Kazanıldı' or new_stage.name == 'Won'):
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
                    'name': f'{lead.name} Etkinlik Günü',
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