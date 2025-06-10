from odoo import models, fields, api
from datetime import date, datetime
from odoo.exceptions import ValidationError

class CrmLead(models.Model):
    _inherit = "crm.lead"

    option1 = fields.Date(string="Alternatif Tarih 1")
    option2 = fields.Date(string="Alternatif Tarih 2")
    option3 = fields.Date(string="Alternatif Tarih 3")
    wedding_type = fields.Many2one(
        comodel_name="wedding.type",
        string="Düğün Tipi",
        ondelete="set null",
    )
    request_date = fields.Date(string="Teklif Tarihi")
    wedding_year = fields.Char(
        string="Düğün Yılı",
        size=4,
        help="Düğün yılı (2025-2100 arası)"
    )
    people = fields.Integer(string="Kişiler")
    second_contact = fields.Many2one(
        comodel_name="res.partner",
        string="İkincil Kontakt",
        ondelete="set null",
    )
    second_phone = fields.Char(string="İkincil Telefon")
    second_mail = fields.Char(string="İkincil Mail")
    second_job_positino = fields.Char(string="İkincil İş Pozisyonu")


    
    @api.constrains('wedding_year')
    def _check_wedding_year(self):
        if self.wedding_year:
            if not self.wedding_year.isdigit():
                raise ValidationError("Düğün yılı sadece sayı içermelidir.")
            
            if len(self.wedding_year) != 4:
                raise ValidationError("Düğün yılı 4 haneli olmalıdır.")
            
            year = int(self.wedding_year)
            
            if year < 2024:
                raise ValidationError("Düğün yılı 2024'den büyük olmalıdır (minimum 2025).")
            
            if year > 2100:
                raise ValidationError("Düğün yılı 2100'den küçük olmalıdır (maksimum 2100).")
