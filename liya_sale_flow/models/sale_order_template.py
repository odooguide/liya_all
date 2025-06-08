from odoo import api, fields, models

class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    project_task_ids = fields.One2many(
        comodel_name='sale.order.template.task',
        inverse_name='sale_order_template_id',
        string='Project Tasks',
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
    description = fields.Text(string='Task Description')
    stage_id = fields.Many2one(
        comodel_name='project.task.type',
        string='Stage',
    )
    planned_date = fields.Selection(
        selection=[
            ('before_wedding', 'Düğünden Önce'),
            ('after_wedding', 'Düğünden Sonra'),
        ],
        string='Planned Date',
        default='before_wedding',
    )
    days = fields.Integer(string='Days')
    user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Assignees',
        help="Birden fazla kullanıcıyı atayabilirsiniz."
    )
    activity_type_id = fields.Many2one(
        comodel_name='mail.activity.type',
        string='Activity Type',
    )
    optional_product_id = fields.Many2one(
        'product.product',
        string='Koşul',
        help="Bu template için tanımlı Optional Products listesinden seçin."
    )
