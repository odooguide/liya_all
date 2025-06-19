from odoo import fields,models

class EventEvent(models.Model):
    _name='event.event'

    name=fields.Char(string='Event Name')
    start_date=fields.Datetime(string='Start Date')
    end_date=fields.Datetime(string='End Date')

    template_id = fields.Many2one(
        comodel_name='sale.order.template',
        string='Template',
        ondelete='cascade',
    )
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
        ondelete='cascade',
    )