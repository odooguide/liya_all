from odoo import models, fields
from datetime import date

class CrmLead(models.Model):
    _inherit = "crm.lead"

    def _get_year_selection(self):
        current_year = date.today().year
        return [(str(y), str(y)) for y in range(current_year - 100, current_year + 11)]

    option1 = fields.Date(string="Option 1")
    option2 = fields.Date(string="Option 2")
    option3 = fields.Date(string="Option 3")
    wedding_type = fields.Many2one(
        comodel_name="wedding.type",
        string="Wedding Type",
        ondelete="set null",
    )
    request_date = fields.Date(string="Request Date")
    wedding_year = fields.Selection(
        selection=_get_year_selection,
        string="Düğün Yılı",
        help="Sadece yıl seçilebilen alan",
    )
    people = fields.Integer(string="People")
    second_contact = fields.Many2one(
        comodel_name="res.partner",
        string="Second Contact",
        ondelete="set null",
    )
    second_phone = fields.Char(string="Second Phone")
    second_mail = fields.Char(string="Second Mail")
    second_job_positino = fields.Char(string="Second Job Position")


