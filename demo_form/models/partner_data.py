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
    opportunity_name=fields.Char(string='İsim')
    first_phone = fields.Char(string='First Phone')
    second_phone = fields.Char(string='Second Phone')
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
class Studio345(models.Model):
    _name = 'studio.345'
    _description = 'Studio 345'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Tarih')
    opportunity_name=fields.Char(string='İsim')
    first_phone = fields.Char(string='Birincil Telefon')
    second_phone = fields.Char(string='İkincil Telefon')
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    photo_studio=fields.Char('Ekip')

class GarageCaddebostan(models.Model):
    _name = 'garage.caddebostan'
    _description = 'Garage Caddebostan'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Tarih')
    opportunity_name=fields.Char(string='İsim')
    first_phone = fields.Char(string='Birincil Telefon')
    second_phone = fields.Char(string='İkincil Telefon')
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    photo_studio=fields.Char('Ekip')

class Backlight(models.Model):
    _name = 'backlight'
    _description = 'backlight'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Tarih')
    opportunity_name=fields.Char(string='İsim')
    first_phone = fields.Char(string='Birincil Telefon')
    second_phone = fields.Char(string='İkincil Telefon')
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    first_mail = fields.Char(string='Birincil Mail')
    second_mail = fields.Char(string='Birincil Mail')
    drone=fields.Char('Drone')
    home_exit=fields.Char('Evden Çıkış')
