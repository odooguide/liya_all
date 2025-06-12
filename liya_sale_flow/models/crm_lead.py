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
    request_date = fields.Date(string="Talep Tarihi")
    wedding_year = fields.Char(
        string="Düğün Yılı",
        size=4,
        help="Düğün yılı (2025-2100 arası)"
    )
    people = fields.Integer(string="Kişiler")
    second_contact = fields.Char(
        string="İkincil Kontakt",
    )
    second_phone = fields.Char(string="İkincil Telefon")
    second_mail = fields.Char(string="İkincil Mail")
    second_job_positino = fields.Char(string="İkincil İş Pozisyonu")

    type = fields.Selection(
        [('lead', 'Lead'), ('opportunity', 'Opportunity')],
        compute='_compute_type',
        store=True,
        readonly=False,
    )

    
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

    #Delete related sale orders when lost reason activated
    def action_set_lost(self, **additional_values):
        res = super(CrmLead, self).action_set_lost()

        self.mapped('order_ids').action_cancel()

        return res

    @api.depends('activity_type_id')
    def _compute_type(self):
        for lead in self:
            display = lead.activity_type_id and lead.activity_type_id.display_name or ''
            if 'Meeting' in display:
                lead.type = 'opportunity'
            else:
                lead.type='lead'
        return None