from odoo import models,api,fields, _
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime
from odoo.tools.misc import formatLang
from babel.dates import format_date as babel_format_date


class SaleOrder(models.Model):
    _inherit='sale.order'


    is_project_true=fields.Boolean(string='Is There Any Project?')
    confirmed_contract=fields.Binary(string="Signed Contract")
    coordinator_ids = fields.Many2many(comodel_name='res.partner', string="Coordinators",
                                       domain=[('employee_ids', '!=', False)])
    wedding_date=fields.Date(string="Event Date")
    people_count=fields.Integer(string="People Count")
    second_contact=fields.Char(string="Secondary Contact")
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
    event_type=fields.Char(string="Type of Invitation")

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        sale_order_template_id = (
                defaults.get('sale_order_template_id')
                or self.env.context.get('default_sale_order_template_id')
        )
        if sale_order_template_id:
            tmpl = self.env['sale.order.template'].browse(sale_order_template_id)
            if tmpl.template_type == 'event':
                defaults['service_ids'] = [
                    (0, 0, {
                        'name': svc.name,
                        'description': svc.description,
                    })
                    for svc in tmpl.service_ids
                ]
                defaults['program_ids'] = [
                    (0, 0, {
                        'name': prog.name,
                        'start_datetime': prog.start_datetime,
                        'end_datetime': prog.end_datetime,
                    })
                    for prog in tmpl.program_ids
                ]
                # transport_ids
                defaults['transport_ids'] = [
                    (0, 0, {
                        'departure_location': tr.departure_location,
                        'arrival_location': tr.arrival_location,
                        'arrival_datetime': tr.arrival_datetime,
                    })
                    for tr in tmpl.transport_ids
                ]
        return defaults

    @api.onchange('sale_order_template_id')
    def _onchange_sale_order_template_id(self):
        if self.sale_order_template_id and self.sale_order_template_id.template_type == 'event':
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
        res=super().action_confirm()
        for order in self:
            if not order.coordinator_ids:
                raise UserError(_("Koordinatör seçilmeden bu teklifi onaylayamazsınız. Lütfen koordinatör seçin."))
        return res



    def action_project_create(self):
        self.ensure_one()

        if self.project_id:
            return True

        seq_num = self.env['ir.sequence'].next_by_code('sale.order.project') or '0000'
        today = fields.Date.context_today(self)
        date_str = today.strftime('%Y-%m-%d')
        partner_slug = self.partner_id.name.replace(' ', '-')
        project_name = f"D{seq_num}-{date_str}-{partner_slug}"

        vals = {
            'name': project_name,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id.id or self.env.uid,
            'allow_billable': True,
            'privacy_visibility': 'portal',
            'sale_order_id': self.id,
        }

        project = self.env['project.project'].create(vals)

        self.project_id = project.id

        self.is_project_true=True

        return True

    @api.onchange('project_id')
    def _is_project(self):

        project_id=self.project_id
        if project_id:
            self.is_project_true=True
        else:
            self.is_project_true=False

    @api.model_create_multi
    def create(self, vals):
        sale = super().create(vals)
        if sale.opportunity_id:
            sale_model = self.env['ir.model'].sudo().search(
                [('model', '=', 'sale.order')], limit=1)

            activity_types = self.env['mail.activity.type'].search(
                [('is_quot', '=', True)])

            for atype in activity_types:
                self.env['mail.activity'].create({
                    'res_model_id': sale_model.id,
                    'res_model': 'sale.order',
                    'res_id': sale.id,
                    'activity_type_id': atype.id,
                    'user_id': sale.user_id.id or sale.create_uid.id,
                    'date_deadline': date.today(),
                })

        return sale

    def action_quotation_sent(self):
        action = super(SaleOrder, self).action_quotation_sent()
        for sale in self:
            if sale.opportunity_id:
                sale_model = self.env['ir.model'].sudo().search(
                    [('model', '=', 'sale.order')], limit=1)
                activity_types = self.env['mail.activity.type'].search(
                    [('is_reminder', '=', True)])
                for atype in activity_types:
                    self.env['mail.activity'].create({
                        'res_model_id': sale_model.id,
                        'res_model': 'sale.order',
                        'res_id': sale.id,
                        'activity_type_id': atype.id,
                        'user_id': sale.user_id.id or sale.create_uid.id,
                        'date_deadline': date.today() + timedelta(days=2),
                    })
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

