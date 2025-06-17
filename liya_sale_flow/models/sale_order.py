from odoo import models,api,fields,_
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime
from odoo.tools.misc import formatLang
from babel.dates import format_date as babel_format_date


class SaleOrder(models.Model):
    _inherit='sale.order'

    project_task_ids = fields.Many2many(
        comodel_name='sale.order.template.task',
        string='Projedeki Görevler',
        compute='_compute_project_task_ids',
    )
    is_project_true=fields.Boolean(string='Is There Any Project?')
    confirmed_contract=fields.Binary(string="Onaylı Sözleşme")
    coordinator_ids = fields.Many2many(comodel_name='res.partner', string="Koordinatörler",
                                       domain=[('employee_ids', '!=', False)])
    wedding_date=fields.Date(string="Etkinlik Tarihi")
    people_count=fields.Integer(string="Kişi Sayısı")
    second_contact=fields.Char(string="İkinci Kontak")
    wedding_day = fields.Char(
        string='Dugun Gunu',
        compute='_compute_wedding_day',
        store=True,
    )
    wedding_date_display = fields.Char(
        string="Etkinlik Tarihi (Formatlı)",
        compute='_compute_wedding_date_display',
        store=True,
    )

    @api.depends('wedding_date')
    def _compute_wedding_date_display(self):
        for order in self:
            if order.wedding_date:
                lang = 'tr'
                order.wedding_date_display = babel_format_date(
                    order.wedding_date,
                    format='d MMMM y, EEEE',
                    locale=lang.replace('_', '-')
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

    @api.depends('sale_order_template_id', 'order_line.product_id')
    def _compute_project_task_ids(self):
        for order in self:
            if not order.sale_order_template_id:
                order.project_task_ids = False
                continue
            tasks = order.sale_order_template_id.project_task_ids
            prod_ids = order.order_line.mapped('product_id.id')

            valid = tasks.filtered(
                lambda t: not t.optional_product_id
                          or t.optional_product_id.id in prod_ids
            )
            order.project_task_ids = valid





    # def action_confirm(self):
    #
    #     res = super().action_confirm()
    #     for order in self:
    #         if order.sale_order_template_id:
    #             if not order.project_id:
    #                 raise UserError(_(
    #                     "Sipariş %s için proje oluşturulmamış. "
    #                     "Önce bir proje atanmalı."
    #                 ) % order.name)
    #             for tmpl in order.project_task_ids:
    #                 self.env['project.task'].create({
    #                     'project_id': order.project_id.id,
    #                     'name': tmpl.name,
    #                     'description': tmpl.description,
    #                     'stage_id': tmpl.stage_id.id,
    #                     'user_ids': [(6, 0, tmpl.user_ids.ids)],
    #                 })
    #     return res

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

    @api.model
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
