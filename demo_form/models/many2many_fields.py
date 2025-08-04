from odoo import models, fields


class TransportPort(models.Model):
    _name = 'project.transport.port'
    _description = 'Transport Port'

    name = fields.Char(string="Port Name", required=True)


class DemoMenuDessert(models.Model):
    _name = 'project.demo.menu.dessert'
    _description = "Demo Menu Dessert Option"

    name = fields.Char(string="Dessert Name", required=True)

class DemoMenuDessert(models.Model):
    _name = 'project.demo.menu.dessert.ultra'
    _description = "Demo Menu Dessert Ultra"

    name = fields.Char(string="Dessert Name", required=True)


class DemoMenuMeze(models.Model):
    _name = 'project.demo.menu.meze'
    _description = "Demo Menu Appetizer (Meze)"

    name = fields.Char(string="Appetizer Name", required=True)


class TableTheme(models.Model):
    _name = 'project.demo.table.theme'
    _description = "Table Theme Option"
    name = fields.Char(string="Theme", required=True)


class TableCharger(models.Model):
    _name = 'project.demo.table.charger'
    _description = "Table Charger Option"
    name = fields.Char(string="Charger Type", required=True)


class RunnerDesign(models.Model):
    _name = 'project.demo.runner.design'
    _description = "Runner Design Option"
    name = fields.Char(string="Cloth & Runner Design", required=True)


class TableColor(models.Model):
    _name = 'project.demo.table.color'
    _description = "Table Color Option"
    name = fields.Char(string="Color Choice", required=True)


class CeremonyTag(models.Model):
    _name = 'project.demo.ceremony.tag'
    _description = "Ceremony Tag Option"
    name = fields.Char(string="Ceremony Tag", required=True)


class CakeChoice(models.Model):
    _name = 'project.demo.cake.choice'
    _description = "Cake Choice Option"
    name = fields.Char(string="Cake Choice", required=True)
