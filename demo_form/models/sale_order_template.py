from odoo import api, fields, models


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    project_task_ids = fields.One2many(
        comodel_name='sale.order.template.task',
        inverse_name='sale_order_template_id',
        string='Project Tasks',
    )
    schedule_line_ids = fields.One2many(
        'sale.order.template.schedule.line',
        'sale_template_id',
        string="Schedule Lines",
        help="Scheduled events for this template"
    )
    transport_line_ids = fields.One2many(
        'sale.order.template.transport.line',
        'sale_template_id',
        string="Transport Lines",
        help="Transport steps for this template"
    )


class SaleOrderTemplateTask(models.Model):
    _name = 'sale.order.template.task'
    _description = 'Sale Order Template Task'

    sale_order_template_id = fields.Many2one(
        comodel_name='sale.order.template',
        string='Sale Order Template',
        ondelete='cascade',
    )
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
        ondelete='cascade',
    )
    name = fields.Char(string='Task Name', required=True)
    description = fields.Text(string='Description')
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
    event_date=fields.Date(string='Event Date')

class SaleOrderTemplateScheduleLine(models.Model):
    _name = 'sale.order.template.schedule.line'
    _description = "Sale Order Template Schedule Line"

    sale_template_id = fields.Many2one(
        'sale.order.template', ondelete='cascade')
    sequence = fields.Integer(string="Step")
    event = fields.Char(string="Event")
    time = fields.Float(string="Time")
    location_type = fields.Selection(
        [('restaurant', 'Restaurant'), ('beach', 'Beach')],
        string="Location Type")
    location_notes = fields.Char(string="Details")

class SaleOrderTemplateTransportLine(models.Model):
    _name = 'sale.order.template.transport.line'
    _description = "Sale Template Transport Line"

    sale_template_id = fields.Many2one(
        'sale.order.template', ondelete='cascade')
    sequence = fields.Integer(string="Step")
    label = fields.Char(string="Description")
    time = fields.Float(string="Time")
    port = fields.Selection(
        [('dragos', 'Dragos'), ('bostanci', 'Bostanci'),
         ('buyukada_dragos', 'Buyukada + Dragos'), ('other', 'Other')],
        string="Port")
    other_port = fields.Char(string="If Other, specify")


