from odoo import fields,models

class MailActivityType(models.Model):
    _inherit='mail.activity.type'

    is_quot=fields.Boolean(string='Teklif için mi?')
    is_reminder=fields.Boolean(string='Teklif Hatirlatma için mi?')