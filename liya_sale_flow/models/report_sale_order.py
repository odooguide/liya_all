# addons/your_module/models/report_saleorder.py
from odoo import api, models, _
from odoo.exceptions import UserError

class ReportSaleorder(models.AbstractModel):
    _name = 'report.sale.report_saleorder'

    @api.model
    def _get_report_values(self, docids, data=None):
        orders = self.env['sale.order'].browse(docids)
        # Eğer herhangi bir siparişte kişi sayısı 0 ise, raporu kes
        if any(order.people_count < 1 for order in orders):
            raise UserError(_(
                "PDF raporu oluşturulamaz: 'Kişi Sayısı' 0 olamaz.\n"
                "PDF report can't be created. People Count can't be 0 or below"
            ))
