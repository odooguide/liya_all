from odoo import fields, models


class BanquetPages(models.Model):
    _name = 'banquet.pages'
    _description = 'Teklif Bölümü'
    _order = 'sequence, name'

    name = fields.Char(string='Bölüm Adı', required=True)
    sequence = fields.Integer(string='Sıra', default=10)
