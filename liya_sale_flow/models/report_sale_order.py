from odoo import api, models, _
from odoo.exceptions import UserError

class ReportSaleorderDocument(models.AbstractModel):
    _inherit = 'report.sale.report_saleorder_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        orders = self.env['sale.order'].browse(docids)
        if any(order.people_count < 1 for order in orders):
            raise UserError(_(
                "PDF raporu oluşturulamaz: 'Kişi Sayısı' 0 olamaz.\n"
                "PDF report can't be created. People Count can't be 0 or below"
            ))
        return super(ReportSaleorderDocument, self)._get_report_values(docids, data=data)
