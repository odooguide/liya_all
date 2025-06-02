from odoo import models, fields

class CrmLead(models.Model):
    _inherit = "crm.lead"

    option1 = fields.Date(string="Option 1")
    option2 = fields.Date(string="Option 2")
    option3 = fields.Date(string="Option 3")
    wedding_type = fields.Many2one(
        comodel_name="wedding.type",
        string="Wedding Type",
        ondelete="set null",
    )
    request_date = fields.Date(string="Request Date")
    wedding_year = fields.Date(string="Wedding Year")
    people = fields.Integer(string="People")
    second_contact = fields.Many2one(
        comodel_name="res.partner",
        string="Second Contact",
        ondelete="set null",
    )
    second_phone = fields.Char(string="Second Phone")
    second_mail = fields.Char(string="Second Mail")
    second_job_positino = fields.Char(string="Second Job Position")