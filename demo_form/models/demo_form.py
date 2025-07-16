from odoo import models, fields


class DemoForm(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'demo.form'
    _description = 'Demo Form'
