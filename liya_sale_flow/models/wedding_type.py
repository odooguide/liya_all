from odoo import models, fields

class WeddingType(models.Model):
    _name = "wedding.type"
    _description = "Düğün Tipi"

    name = fields.Char(string="Etkinlik Tipi Adı", required=True)