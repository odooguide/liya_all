from odoo import fields,models

class EventEvent(models.Model):
    _name='event.event'

    name=fields.Char(string='Etkinlik Adı')
    start_date=fields.Datetime(string='Etkinlik Başlangıcı')
    end_date=fields.Datetime(string='Etkinlik Bitişi')

    template_id = fields.Many2one(
        comodel_name='sale.order.template',
        string='Şablon',
        ondelete='cascade',
    )
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sipariş',
        ondelete='cascade',
    )