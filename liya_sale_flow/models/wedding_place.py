from odoo import models,fields

class WeddingPlace(models.Model):
    _name='wedding.place'
    _description='Wedding Place'

    name=fields.Char(string="Type")