from odoo import api,fields,models,_
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit='sale.order.line'

    tag_ids=fields.Many2many(related='order_id.tag_ids',string='Tag Ids')

    @api.onchange('product_template_id')
    def _onchange_order_line_template(self):
        if not self.order_id.sale_order_template_id:
            raise UserError(_("Lütfen teklif şablonunu seçin!."))
