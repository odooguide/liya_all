from odoo import fields, models


class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    allowed_ip_ids = fields.One2many('allowed.ips', 'user_ip_id',
                                     string='IP Address',
                                     help="Allowed ip addresses for the user.")
