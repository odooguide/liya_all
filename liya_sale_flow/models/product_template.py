from odoo import fields,models

class ProductTemplate(models.Model):
    _inherit='product.template'

    is_wedding=fields.Boolean(string="Düğün Ürünü mü?")
