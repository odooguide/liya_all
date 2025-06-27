from odoo import  fields, models

class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    template_type = fields.Selection([
        ('wedding', 'Düğün'),
        ('event', 'Etkinlik'),
    ], string='Template Type', default='wedding')

    service_ids = fields.One2many(
        comodel_name='sale.order.service',
        inverse_name='sale_order_template_id',
        string='Services',
    )
    program_ids = fields.One2many(
        comodel_name='sale.order.program',
        inverse_name='sale_order_template_id',
        string='Program Flow',

    )

    transport_ids = fields.One2many(
        comodel_name='sale.order.transport',
        inverse_name='sale_order_template_id',
        string='Transportation'
    )

