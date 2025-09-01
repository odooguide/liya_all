from odoo import api, fields, models

class WeddingTrio(models.Model):
    _name = 'wedding.trio'
    _description = 'Wedding Trio'

    name = fields.Char(string='Name', required=True)
    time = fields.Char(string='Time')
    date = fields.Date(string='Event Date')
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    port_ids = fields.Many2many(
        'project.transport.port',
        'wedding_trio_port_rel',
        'trio_id',
        'port_id',
        string='Ports',
    )

class BlueMarmara(models.Model):
    _name = 'blue.marmara'
    _description = 'Blue Marmara'

    name = fields.Char(string='Name', required=True)
    guest_count = fields.Char(string='Guest Count')
    date = fields.Date(string='Event Date')
    boat = fields.Char(string="Boat")
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )

class PartnerVedans(models.Model):
    _name = 'partner.vedans'
    _description = 'Partner Vedans'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Event Date')
    first_phone = fields.Char(string='First Phone')
    second_phone = fields.Char(string='Second Phone')
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )