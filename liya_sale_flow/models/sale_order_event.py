from odoo import models, fields, api, _
from datetime import datetime, timedelta


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
    start_datetime = fields.Char(string='Start Time')
    end_datetime = fields.Char(string='End Time' )
    hours = fields.Char(
        string='Duration (hours)',
        compute='_compute_hours',
        store=True,
    )

    @api.depends('start_datetime', 'end_datetime')
    def _compute_hours(self):
        fmt = '%H:%M'
        for rec in self:
            sd = rec.start_datetime
            ed = rec.end_datetime
            if sd and ed:
                try:
                    t1 = datetime.strptime(sd, fmt)
                    t2 = datetime.strptime(ed, fmt)
                except ValueError:
                    rec.hours = False
                    continue

                if t2 < t1:
                    t2 += timedelta(days=1)

                diff = t2 - t1
                h = diff.seconds // 3600
                m = (diff.seconds % 3600) // 60
                rec.hours = '{}:{:02d}'.format(h, m)
            else:
                rec.hours = False


class SaleOrderTransport(models.Model):
    _name = 'sale.order.transport'
    _description = 'Sale Order Transportation'

    order_id = fields.Many2one('sale.order', string='Order')
    sale_order_template_id = fields.Many2one('sale.order.template', string='Sale Order Template')
    departure_location = fields.Char(string='Departure Location')
    arrival_location = fields.Char(string='Arrival Location')
    arrival_datetime = fields.Char(string='Departure Time')
