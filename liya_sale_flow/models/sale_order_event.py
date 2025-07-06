from odoo import models, fields, api, _


class SaleOrderService(models.Model):
    _name = 'sale.order.service'
    _description = 'Sale Order Services'

    order_id = fields.Many2one('sale.order', string='Order')
    sale_order_template_id = fields.Many2one('sale.order.template', string='Sale Order Template')
    name = fields.Char(string='Service Name', )
    description = fields.Text(string='Description')


class SaleOrderProgram(models.Model):
    _name = 'sale.order.program'
    _description = 'Sale Order Program Flow'

    order_id = fields.Many2one('sale.order', string='Order')
    sale_order_template_id = fields.Many2one('sale.order.template', string='Sale Order Template')
    name = fields.Char(string='Event Name', )
    start_datetime = fields.Datetime(string='Start Time', )
    end_datetime = fields.Datetime(string='End Time', )
    hours = fields.Char(string='Duration (hours)', store=True)


class SaleOrderTransport(models.Model):
    _name = 'sale.order.transport'
    _description = 'Sale Order Transportation'

    order_id = fields.Many2one('sale.order', string='Order')
    sale_order_template_id = fields.Many2one('sale.order.template', string='Sale Order Template')
    departure_location = fields.Char(string='Departure Location')
    arrival_location = fields.Char(string='Arrival Location')
    arrival_datetime = fields.Datetime(string='Departure Time')
