from odoo import fields,models

class MailActivityType(models.Model):
    _inherit='mail.activity.type'

    is_quot=fields.Boolean(string='Is Quotation?')
    is_reminder=fields.Boolean(string='Is Quotation Reminder?')
    is_event=fields.Boolean(string='Is Event?')