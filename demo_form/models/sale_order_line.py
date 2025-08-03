from odoo import models, api, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def _onchange_product_id_optional(self):
        for line in self:
            if not line.product_id or not line.order_id:
                continue
            tmpl = line.product_id.product_tmpl_id.id
            if tmpl in line.order_id.sale_order_option_ids.product_id.ids:
                raise UserError(_('Lütfen bu ürünü optional products bölümünden seçin.'))
