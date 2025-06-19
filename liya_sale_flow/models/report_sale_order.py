# addons/your_module/models/report_saleorder.py
from odoo import api, models, _
from odoo.exceptions import UserError

class ReportSaleorder(models.AbstractModel):
    _name = 'report.sale.report_saleorder'

    @api.model
    def _get_report_values(self, docids, data=None):
        orders = self.env['sale.order'].browse(docids)
        # invalidse hata fırlat
        if any(order.people_count < 1 for order in orders):
            raise UserError(_(
                "PDF raporu oluşturulamaz: 'Kişi Sayısı' 0 olamaz.\n"
                "PDF report can't be created. People Count can't be 0 or below"
            ))
        # geçerliyse, orijinal rapor değerlerini aynen döndür
        return super()._get_report_values(docids, data=data)
