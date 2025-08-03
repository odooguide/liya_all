from odoo import api, fields, models
from datetime import timedelta, date, datetime


class SaleProjectTask(models.Model):
    _name = 'sale.project.task'
    _description = 'Sale Project Task'

    name = fields.Char(string='Task Name', required=True)
    description = fields.Text(string='Description')
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
        ondelete='cascade',
    )
    stage_id = fields.Many2one(
        comodel_name='project.task.type',
        string='Stage',
    )
    planned_date = fields.Selection(
        selection=[
            ('before_wedding', 'Before Wedding'),
            ('border', 'Border Date'),
            ('casual_date', 'Stable Date'),
        ],
        string='Planned Type',
        default='before_wedding',
    )
    deadline_date = fields.Date(string='Deadline Date')
    date_line = fields.Char(string='Date Line')
    days = fields.Integer(string='Days')
    user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Responsibles',

    )
    email_template_id = fields.Many2one(
        comodel_name='mail.template',
        domain=[('model_id.model', '=', 'project.task')],
        string='E-mail Template',

    )
    optional_product_id = fields.Many2one(
        'product.product',
        string='Optional Products',
    )
    communication_type = fields.Selection(selection=[
        ('mail', 'E-Mail'),
        ('phone', 'Whatsapp'),
    ],
        string='Communication Type',
        default='phone', )
    event_date = fields.Date(string='Event Date')

    @api.onchange('planned_date', 'days', 'date_line', 'event_date')
    def _onchange_deadline_date(self):
        for rec in self:
            today = fields.Date.today()
            if rec.sale_order_id.wedding_date:
                wedd = rec.sale_order_id.wedding_date
                if rec.planned_date == 'before_wedding':
                    if wedd and rec.days:
                        rec.deadline_date = wedd - timedelta(days=rec.days)
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
                        same_year = (wedd.year == today.year)
                    except ValueError:
                        wedd = None
                    if same_year and wedd and wedd > base_dt and today > base_dt:
                        target = today + timedelta(days=rec.days)

                    else:
                        target = base_dt
                        if target <= today:
                            target = date(today.year + 1, month, day)
                    rec.deadline_date = target
                    continue
