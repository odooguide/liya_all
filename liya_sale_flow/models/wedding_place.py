from odoo import models,fields

class WeddingPlace(models.Model):
    _name='wedding.place'

    name=fields.Char(string="Type")