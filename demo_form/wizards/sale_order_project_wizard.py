from odoo import api, fields, models
from datetime import timedelta, date


class SaleOrderProjectWizard(models.TransientModel):
    _name = 'sale.order.project.wizard'
    _description = 'Wizard for creating project from Sale Order'

    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
        required=True,
        ondelete='cascade',
    )
    lead_id=fields.Many2one('crm.lead',string='CRM Lead ID')
    project_task_line_ids = fields.One2many(
        comodel_name='sale.order.project.wizard.line',
        inverse_name='wizard_id',
        string='Tasks Which Will Be Add to Project',
    )



    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        order_id = self.env.context.get('default_sale_order_id')
        if order_id and 'project_task_line_ids' in fields_list:
            order = self.env['sale.order'].browse(order_id)
            lines = [
                (0, 0, {
                    'task_id': task.id,
                    'name': task.name,
                    'description':task.description,
                    'stage_id':task.stage_id.id,
                    'planned_date':task.planned_date,
                    'date_line':task.date_line,
                    'days':task.days,
                    'deadline_date':task.deadline_date,
                    'user_ids':task.user_ids.ids,
                    'email_template_id':task.email_template_id.id,
                    'optional_product_id':task.optional_product_id.id,
                    'communication_type':task.communication_type,
                    
                })
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
        date_str = order.wedding_date.strftime('%d-%m-%Y')
        partner_slug = (order.opportunity_id and order.opportunity_id.name or '').replace(' ', '-')
        project_name = f"D{seq_num}-{date_str}-{partner_slug}"

        vals = {
            'name': project_name,
            'partner_id': order.partner_id.id,
            'company_id': order.company_id.id,
            'user_id': order.user_id.id or self.env.uid,
            'allow_billable': True,
            'privacy_visibility': 'portal',
            'reinvoiced_sale_order_id': order.id,
            'sale_line_id': order.order_line and order.order_line[0].id or False
        }


        project = self.env['project.project'].create(vals)
        done_stage = self.env['project.task.type'].search([
            ('project_ids', 'in', project.id),
            ('name', '=', 'Done')
        ], limit=1)
        if not done_stage:
            done_stage = self.env['project.task.type'].create({
                'name': 'Done',
                'sequence':10,
                'project_ids': [(4, project.id)],
            })
        order.project_id = project.id

        lcv_subtasks = [
            'Çifte LCV Listesi Paylaş',
            'LCV Listesi çift tarafından dolduruldu',
            'LCV Aranıyor',
            'Raporlandı',
            'Yedek liste',
            'Oturma Planı paylaşıldı',
        ]

        for tmpl in self.project_task_line_ids:
            if tmpl.user_ids:
                responsibles = tmpl.user_ids.ids
            else:
                user_recs = order.coordinator_ids.mapped('employee_ids.user_id')
                users = self.env['res.users'].search([
                    ('id', 'in', user_recs.ids)
                ])
                responsibles = users.ids

            sale_line = order.order_line.filtered(lambda l: l.product_id == tmpl.optional_product_id)
            sale_line_id = sale_line and sale_line[0].id or False

            new_task = self.env['project.task'].create({
                'project_id': project.id,
                'name': tmpl.name,
                'description': tmpl.description,
                'stage_id': tmpl.stage_id.id,
                'user_ids': [(6, 0, responsibles)],
                'date_deadline': tmpl.deadline_date,
                'email_template_id': tmpl.email_template_id.id,
                'communication_type': tmpl.communication_type,
                'sale_line_id': sale_line_id,
            })
            if tmpl.communication_type == 'phone' and tmpl.email_template_id:
                template = tmpl.email_template_id
                new_task.message_post(
                    body=template.body_html,
                    subtype_xmlid='mail.mt_comment'
                )

            if 'lcv' in tmpl.name.lower():
                for sub_name in lcv_subtasks:
                    self.env['project.task'].create({
                        'project_id': project.id,
                        'name': sub_name,
                        'parent_id': new_task.id,
                        'user_ids': [(6, 0, responsibles)],

                    })

        order.is_project_true = True
        order.opportunity_id.project_id=project.id
        order.opportunity_id.action_set_won()

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
        comodel_name='sale.project.task',
        string='Project Template',
        required=False,
    )
    sale_order_id=fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order Id',
        required=False,
    )
    name = fields.Char(
        string='Task Name'
    )
    description = fields.Text(
        string='Description'
    )
    stage_id = fields.Many2one(
        comodel_name='project.task.type',
        string='Stage'
    )
    planned_date = fields.Selection(
        selection=[
            ('before_wedding', 'Before Wedding'),
            ('border', 'Border Date'),
            ('casual_date', 'Stable Date'),
        ],
        string='Planned Type'
    )
    date_line = fields.Char(
        string='Border Date Line'
    )
    days = fields.Integer(
        string='Days'
    )
    deadline_date = fields.Date(
        string='Deadline Date'
    )
    user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Responsibles',
        help="Birden fazla kullanıcıyı atayabilirsiniz."
    )
    email_template_id = fields.Many2one(
        comodel_name='mail.template',
        string='E-Mail Template'
    )
    optional_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Optional Product',
    )
    communication_type = fields.Selection(
        selection=[
            ('mail', 'E-Mail'),
            ('phone', 'Whatsapp'),
        ],
        string='Communication Type',
    )



    @api.onchange('planned_date', 'days', 'date_line', 'event_date')
    def _onchange_deadline_date(self):
        for rec in self:
            today = fields.Date.today()
            wedding_date=rec.wizard_id.sale_order_id.wedding_date
            if wedding_date:
                if rec.planned_date == 'before_wedding':
                    if wedding_date and rec.days:
                        rec.deadline_date = wedding_date - timedelta(days=rec.days)
                    else:
                        rec.deadline_date = False

                elif rec.planned_date == 'border':

                    if not rec.date_line:
                        rec.deadline_date = False
                        continue
                    try:
                        day_str, month_str = rec.date_line.split('.')
                        day, month = int(day_str), int(month_str)
                    except (ValueError, AttributeError):
                        rec.deadline_date = False
                        continue

                    try:
                        base_dt = date(today.year, month, day)
                    except ValueError:
                        rec.deadline_date = False
                        continue
                    same_year = False
                    try:
                        same_year = (wedding_date.year == today.year)
                    except ValueError:
                        wedding_date = None
                    if same_year and wedding_date and wedding_date > base_dt and today > base_dt:
                        target = today + timedelta(days=1)

                    else:
                        target = base_dt
                        if target <= today:
                            target = date(today.year + 1, month, day)
                    rec.deadline_date = target
                    continue

