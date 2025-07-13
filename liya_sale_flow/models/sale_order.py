from odoo import models, api, fields, _
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime
from odoo.tools.misc import formatLang
from babel.dates import format_date as babel_format_date


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    confirmed_contract = fields.Binary(string="Signed Contract")
    confirmed_contract_name = fields.Char(string="Contract Filename")
    coordinator_ids = fields.Many2many(comodel_name='res.partner', string="Coordinators",
                                       domain=[('employee_ids', '!=', False)])
    wedding_date = fields.Date(string="Event Date")
    people_count = fields.Integer(string="People Count")
    second_contact = fields.Char(string="Secondary Contact")
    wedding_day = fields.Char(
        string='Event Day',
        compute='_compute_wedding_day',
        store=True,
    )
    wedding_date_display = fields.Char(
        string="Event Date (Formatted)",
        compute='_compute_wedding_date_display',
        store=True,
    )
    service_ids = fields.One2many(
        comodel_name='sale.order.service',
        inverse_name='order_id',
        string='Services',
    )
    program_ids = fields.One2many(
        comodel_name='sale.order.program',
        inverse_name='order_id',
        string='Program Flow',
    )
    transport_ids = fields.One2many(
        comodel_name='sale.order.transport',
        inverse_name='order_id',
        string='Transportation'
    )
    contract_date = fields.Date(string='Contract Date')
    event_type = fields.Char(string="Type of Invitation")
    is_event_selected = fields.Boolean(string="Is Event Template Selected", store=True)

    duration_display = fields.Char(
        string='Toplam Süre',
        store=True,
    )
    banquet_pages = fields.Many2many('banquet.pages', string='Banquet Sayfaları')

    @api.onchange('confirmed_contract')
    def _onchange_confirmed_contract_security(self):
        for rec in self:
            origin = rec._origin
            if origin.confirmed_contract and not self.env.user.has_group('base.group_system'):
                rec.confirmed_contract = origin.confirmed_contract
                rec.confirmed_contract_name = origin.confirmed_contract_name
                raise UserError(
                    _('Only administrators can modify or delete the Signed Contract once uploaded.')
                )

    @api.onchange('program_ids', 'program_ids.hours')
    def _onchange_hours(self):
        for record in self:
            total_minutes = 0
            for prog in record.program_ids:
                hours_str = prog.hours or ''
                try:
                    h, m = hours_str.split(':')
                    total_minutes += int(h) * 60 + int(m)
                except ValueError:

                    continue

            hours = total_minutes // 60
            minutes = total_minutes % 60

            parts = []
            if hours:
                parts.append(_("%d Saat") % hours)
            if minutes or not parts:
                parts.append(_("%d Dakika") % minutes)

            record.duration_display = ' '.join(parts)

    @api.onchange('sale_order_template_id')
    def _onchange_sale_order_event_template_id(self):
        if self.sale_order_template_id and self.sale_order_template_id.template_type == 'event':
            self.is_event_selected = True
            self.service_ids = [(5, 0, 0)]
            self.program_ids = [(5, 0, 0)]
            self.transport_ids = [(5, 0, 0)]
            for svc in self.sale_order_template_id.service_ids:
                self.service_ids = [(0, 0, {
                    'name': svc.name,
                    'description': svc.description,
                })]
            for prog in self.sale_order_template_id.program_ids:
                self.program_ids = [(0, 0, {
                    'name': prog.name,
                    'start_datetime': prog.start_datetime,
                    'end_datetime': prog.end_datetime,
                })]
            for tr in self.sale_order_template_id.transport_ids:
                self.transport_ids = [(0, 0, {
                    'departure_location': tr.departure_location,
                    'arrival_location': tr.arrival_location,
                    'arrival_datetime': tr.arrival_datetime,
                })]
        else:
            self.is_event_selected = False
            self.service_ids = [(5, 0, 0)]
            self.program_ids = [(5, 0, 0)]
            self.transport_ids = [(5, 0, 0)]

    @api.depends('wedding_date', 'partner_id.lang')
    def _compute_wedding_date_display(self):
        for order in self:
            if order.wedding_date:
                lang_code = order.partner_id.lang or self.env.lang or 'en'
                locale = lang_code.split('_')[0]
                order.wedding_date_display = babel_format_date(
                    order.wedding_date,
                    format='d MMMM y, EEEE',
                    locale=locale
                )
            else:
                order.wedding_date_display = False

    @api.depends('wedding_date')
    def _compute_wedding_day(self):
        turkish_days = [
            'Pazartesi', 'Salı', 'Çarşamba',
            'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'
        ]
        for rec in self:
            if rec.wedding_date:

                try:
                    date_obj = datetime.strptime(rec.wedding_date, '%Y-%m-%d').date()
                    rec.wedding_day = turkish_days[date_obj.weekday()]
                except (ValueError, TypeError):
                    rec.wedding_day = False
            else:
                rec.wedding_day = False

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            if not order.coordinator_ids and order.team_id.wedding_team:
                raise UserError(_("Koordinatör seçilmeden bu teklifi onaylayamazsınız. Lütfen koordinatör seçin."))
            if not order.wedding_date:
                raise UserError(_("Etkinlik tarihi seçilmeden satışı onaylayamazsınız."))

        return res

    @api.model_create_multi
    def create(self, vals):
        sale = super().create(vals)
        if sale.opportunity_id:
            sale_model = self.env['ir.model'].sudo().search(
                [('model', '=', 'sale.order')], limit=1)
            if sale.team_id.event_team:

                activity_types = self.env['mail.activity.type'].search(
                    [('is_quot', '=', True),
                     ('is_event', '=', True)])

                for atype in activity_types:
                    self.env['mail.activity'].create({
                        'res_model_id': sale_model.id,
                        'res_model': 'sale.order',
                        'res_id': sale.id,
                        'activity_type_id': atype.id,
                        'user_id': sale.user_id.id or sale.create_uid.id,
                        'date_deadline': date.today(),
                    })
            elif not sale.team_id.event_team:

                activity_types = self.env['mail.activity.type'].search(
                    [('is_quot', '=', True),
                     ('is_event', '=', False)])

                for atype in activity_types:
                    self.env['mail.activity'].create({
                        'res_model_id': sale_model.id,
                        'res_model': 'sale.order',
                        'res_id': sale.id,
                        'activity_type_id': atype.id,
                        'user_id': sale.user_id.id or sale.create_uid.id,
                        'date_deadline': date.today(),
                    })
            else:
                return sale

        return sale

    def action_quotation_sent(self):
        action = super(SaleOrder, self).action_quotation_sent()
        for sale in self:
            if sale.opportunity_id:
                if sale.team_id.event_team:
                    sale_model = self.env['ir.model'].sudo().search(
                        [('model', '=', 'sale.order')], limit=1)
                    activity_types = self.env['mail.activity.type'].search(
                        [('is_reminder', '=', True),
                         ('is_event', '=', True)
                         ])

                    for atype in activity_types:
                        self.env['mail.activity'].create({
                            'res_model_id': sale_model.id,
                            'res_model': 'sale.order',
                            'res_id': sale.id,
                            'activity_type_id': atype.id,
                            'user_id': sale.user_id.id or sale.create_uid.id,
                            'date_deadline': date.today() + timedelta(days=2),
                        })
                elif not sale.team_id.event_team:
                    sale_model = self.env['ir.model'].sudo().search(
                        [('model', '=', 'sale.order')], limit=1)
                    activity_types = self.env['mail.activity.type'].search(
                        [('is_reminder', '=', True),
                         ('is_event', '=', False)
                         ])

                    for atype in activity_types:
                        self.env['mail.activity'].create({
                            'res_model_id': sale_model.id,
                            'res_model': 'sale.order',
                            'res_id': sale.id,
                            'activity_type_id': atype.id,
                            'user_id': sale.user_id.id or sale.create_uid.id,
                            'date_deadline': date.today() + timedelta(days=2),
                        })
                else:
                    return action
        return action

    def get_discount_total(self):
        self.ensure_one()
        return sum(line.price_subtotal for line in self.order_line if line.price_subtotal < 0)

    def get_lines_with_options_total(self):
        self.ensure_one()
        total = sum(
            line.price_unit * line.product_uom_qty
            for line in self.order_line
            if line.sale_order_option_ids
        )

    def get_lines_with_options_total_formatted(self):
        self.ensure_one()
        total = sum(
            line.price_unit * line.product_uom_qty
            for line in self.order_line
            if line.sale_order_option_ids
        )
        return formatLang(self.env, total, currency_obj=self.currency_id)

    def get_wedding_net_total(self):
        self.ensure_one()
        return sum(
            line.price_unit * line.product_uom_qty
            for line in self.order_line
            if line.product_id.is_wedding
        )

    def action_custom_send_quotation(self):
        for order in self:
            return order.with_context(hide_default_template=True).action_quotation_send()
