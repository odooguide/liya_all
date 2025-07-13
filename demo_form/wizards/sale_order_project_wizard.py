from odoo import api, fields, models


class SaleOrderProjectWizard(models.TransientModel):
    _name = 'sale.order.project.wizard'
    _description = 'Wizard for creating project from Sale Order'

    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
        required=True,
        ondelete='cascade',
    )
    project_task_line_ids = fields.One2many(
        comodel_name='sale.order.project.wizard.line',
        inverse_name='wizard_id',
        string='Projeye Eklenebilecek Görevler',
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        order_id = self.env.context.get('default_sale_order_id')
        if order_id and 'project_task_line_ids' in fields_list:
            order = self.env['sale.order'].browse(order_id)
            lines = [
                (0, 0, {'task_id': task.id})
                for task in order.project_task_ids
            ]
            res['project_task_line_ids'] = lines
        return res

    def action_confirm_create(self):
        self.ensure_one()
        order = self.sale_order_id

        if order.project_id:
            return {'type': 'ir.actions.act_window_close'}

        seq_num = self.env['ir.sequence'].next_by_code('sale.order.project') or '0000'
        today = fields.Date.context_today(order)
        date_str = today.strftime('%d-%m-%Y')
        partner_slug = (order.opportunity_id and order.opportunity_id.name or '').replace(' ', '-')
        project_name = f"D{seq_num}-{date_str}-{partner_slug}"

        vals = {
            'name': project_name,
            'partner_id': order.partner_id.id,
            'company_id': order.company_id.id,
            'user_id': order.user_id.id or self.env.uid,
            'allow_billable': True,
            'privacy_visibility': 'portal',
            'sale_order_id': order.id,
        }

        project = self.env['project.project'].create(vals)

        order.project_id = project.id



        for tmpl in self.project_task_line_ids:
            if tmpl.user_ids:
                responsibles=tmpl.user_ids.ids
            else:
                responsibles=order.coordinator_ids.ids

            new_task = self.env['project.task'].create({
                'project_id': project.id,
                'name': tmpl.name,
                'description': tmpl.description,
                'stage_id': tmpl.stage_id.id,
                'user_ids': [(6, 0, responsibles)],
                'date_deadline': tmpl.deadline_date,
                'email_template_id': tmpl.email_template_id.id
            })
            if tmpl.communication_type == 'phone' and tmpl.email_template_id:
                template = tmpl.email_template_id
                body_html = template.body_html
                new_task.message_post(
                    body=body_html,
                    subtype_xmlid='mail.mt_comment'
                )

        order.is_project_true = True

        return {'type': 'ir.actions.act_window_close'}


class SaleOrderProjectWizardLine(models.TransientModel):
    _name = 'sale.order.project.wizard.line'
    _description = 'Projeye Eklenebilecek Görev Satırı (Wizard)'

    wizard_id = fields.Many2one(
        comodel_name='sale.order.project.wizard',
        string='Wizard',
        ondelete='cascade',
        required=True,
    )
    task_id = fields.Many2one(
        comodel_name='sale.order.template.task',
        string='Görev Şablonu',
        required=True,
    )
    name = fields.Char(
        related='task_id.name',
        string='Görev Adı',
        readonly=False,
    )
    description = fields.Text(
        related='task_id.description',
        string='Açıklama',
        readonly=False,
    )
    stage_id = fields.Many2one(
        related='task_id.stage_id',
        comodel_name='project.task.type',
        string='Aşama',
        readonly=False,
    )
    planned_date = fields.Selection(
        related='task_id.planned_date',
        selection=[
            ('before_wedding', 'Düğünden Önce'),
            ('border', 'Sınır Tarihi'),
            ('casual_date', 'Sabit Tarih'),
        ],
        string='Planlanan Tarih',
        readonly=False,
    )
    date_line = fields.Char(
        related='task_id.date_line',
        string='Date Line',
        readonly=False,
    )
    days = fields.Integer(
        related='task_id.days',
        string='Gün',
        readonly=False,
    )
    deadline_date = fields.Date(
        related='task_id.deadline_date',
        string='Deadline Date',
        readonly=False,
    )
    user_ids = fields.Many2many(
        related='task_id.user_ids',
        comodel_name='res.users',
        string='Sorumlular',
        readonly=False,
        help="Birden fazla kullanıcıyı atayabilirsiniz."
    )
    email_template_id = fields.Many2one(
        related='task_id.email_template_id',
        comodel_name='mail.template',
        string='E-posta Şablonu',
        readonly=False,
    )
    optional_product_id = fields.Many2one(
        related='task_id.optional_product_id',
        comodel_name='product.product',
        string='Koşul',
        readonly=False,
    )
    communication_type = fields.Selection(
        related='task_id.communication_type',
        selection=[
            ('mail', 'E-Mail'),
            ('phone', 'Whatsapp'),
        ],
        string='Communication Type',
        readonly=False,
    )
