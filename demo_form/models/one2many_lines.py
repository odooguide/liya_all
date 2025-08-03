from odoo import fields, models, api


class DemoTransportLine(models.Model):
    _name = 'project.demo.transport.line'
    _description = "Demo Transport Line"

    demo_form_id = fields.Many2one(
        'project.demo.form', ondelete='cascade')
    sequence = fields.Integer(string="Step")
    label = fields.Char(string="Notes")
    time = fields.Char(string="Time", )
    port_ids = fields.Many2many(
        'project.transport.port',  # the Port model
        'demo_line_port_rel',  # the join table name
        'line_id',  # column in that table → project.demo.transport.line
        'port_id',  # column in that table → project.transport.port
        string="Ports",
    )
    other_port = fields.Char(string="If Other, specify")


class DemoWitnessLine(models.Model):
    _name = 'project.demo.witness.line'
    _description = "Demo Wedding Witness Line"

    demo_form_id = fields.Many2one(
        'project.demo.form', required=True, ondelete='cascade')
    name = fields.Char(string="Name", required=True)
    # phone = fields.Char(string="Phone")


class DemoScheduleLine(models.Model):
    _name = 'project.demo.schedule.line'
    _description = "Demo Schedule Line"

    demo_form_id = fields.Many2one(
        'project.demo.form', ondelete='cascade')
    sequence = fields.Integer(string="Step")
    event = fields.Char(string="Event")
    time = fields.Char(string="Time")
    location_type = fields.Selection(
        [('restaurant', 'Restaurant'), ('beach', 'Beach')],
        string="Location Type")
    location_notes = fields.Char(string="Details")
