from odoo import models, fields, api,_

class SaleOrderService(models.Model):
    _name = 'sale.order.service'
    _description = 'Sale Order Services'

    order_id = fields.Many2one('sale.order', string='Order')
    sale_order_template_id = fields.Many2one('sale.order.template', string='Sale Order Template')
    name = fields.Char(string='Service Name',)
    description = fields.Text(string='Description')


class SaleOrderProgram(models.Model):
    _name = 'sale.order.program'
    _description = 'Sale Order Program Flow'

    order_id = fields.Many2one('sale.order', string='Order')
    sale_order_template_id = fields.Many2one('sale.order.template', string='Sale Order Template')
    name = fields.Char(string='Event Name', )
    start_datetime = fields.Datetime(string='Start Time',)
    end_datetime = fields.Datetime(string='End Time',)
    hours = fields.Float(string='Duration (hours)', compute='_compute_hours', store=True)
    duration_display = fields.Char(
        string='Toplam Süre',
        compute='_compute_total_duration',
        store=False,
    )

    @api.depends('hours')
    def _compute_total_duration(self):
        for rec in self:
            hours_int = int(rec.hours)
            minutes = int(round((rec.hours - hours_int) * 60))
            parts = []
            if hours_int:
                parts.append(_("%d Saat") % hours_int)
            if minutes:
                parts.append(_("%d Dakika") % minutes)
            rec.duration_display = ' '.join(parts) or _("0 Dakika")

    @api.depends('start_datetime', 'end_datetime')
    def _compute_hours(self):
        for rec in self:
            if rec.start_datetime and rec.end_datetime:
                delta = rec.end_datetime - rec.start_datetime
                rec.hours = delta.total_seconds() / 3600.0


class SaleOrderTransport(models.Model):
    _name = 'sale.order.transport'
    _description = 'Sale Order Transportation'

    order_id = fields.Many2one('sale.order', string='Order')
    sale_order_template_id = fields.Many2one('sale.order.template', string='Sale Order Template')
    departure_location = fields.Char(string='Departure Location')
    arrival_location = fields.Char(string='Arrival Location')
    arrival_datetime = fields.Datetime(string='Departure Time')

