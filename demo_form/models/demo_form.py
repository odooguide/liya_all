from odoo import api, fields, models, _

class ProjectDemoForm(models.Model):
    _name = 'project.demo.form'
    _description = "Project Demo Form"

    sale_template_id=fields.Many2one('sale.order.template',string='Event Type')
    project_id = fields.Many2one(
        'project.project', string="Project", ondelete='cascade')
    name = fields.Char(
        string="Reference" ,
        default=lambda self: _('New Demo Form'))
    invitation_owner = fields.Char(string="Invitation Owner")
    invitation_date = fields.Date(string="Invitation Date")
    duration_days = fields.Integer(string="Duration (days)")
    demo_date = fields.Date(string="Demo Date")
    special_notes = fields.Text(string="Special Notes")

    # header fields (example)
    wedding_type = fields.Selection([
        ('mini', "Mini Elite"),
        ('elite', "Elite"),
        ('plus', "Plus"),
        ('ultra', "Ultra")],
        string="Wedding Type")
    guest_count = fields.Integer(string="Guest Count")
    ceremony = fields.Selection([
        ('actual', "Actual"),
        ('staged', "Staged")],
        string="Ceremony Type")
    start_time = fields.Datetime(string="Start Time")
    end_time = fields.Datetime(string="End Time")

    schedule_line_ids = fields.One2many(
        'project.demo.schedule.line', 'demo_form_id',
        string="Schedule")
    transport_line_ids = fields.One2many(
        'project.demo.transport.line', 'demo_form_id',
        string="Transportation")

    # ── Schedule page ─────────────────────────────────────────────────────────
    schedule_description = fields.Html(
        string="Schedule Notes",
        sanitize=True,
        help="Provide notes or instructions for the Schedule page."
    )
    schedule_line_ids = fields.One2many(
        'project.demo.schedule.line', 'demo_form_id',
        string="Schedule Lines"
    )

    # ── Transportation page ───────────────────────────────────────────────────
    transportation_description = fields.Html(
        string="Transportation Notes",
        sanitize=True,
        help="Provide notes or instructions for the Transportation page."
    )
    transport_line_ids = fields.One2many(
        'project.demo.transport.line', 'demo_form_id',
        string="Transport Lines"
    )

    # ── Menu page ─────────────────────────────────────────────────────────────
    menu_description = fields.Html(
        string="Menu Notes",
        sanitize=True,
        help="Provide notes or instructions for the Menu page."
    )
    menu_hot_appetizer = fields.Selection([
        ('lasagna_meat', "Lasagna (Meat)"),
        ('lasagna_vegan', "Lasagna (Vegan)"),
    ], string="Hot Appetizer")
    menu_hot_appetizer_ultra = fields.Selection([
        ('shrimpt', "Shrimp"),
        ('lasagna_vegan', "Lasagna (Vegan)"),
    ], string="Hot Appetizer Ultra")
    menu_dessert_ids = fields.Many2many(
        'project.demo.menu.dessert',
        'demo_form_dessert_rel',
        'form_id',
        'dessert_id',
        string="Dessert Choices",
        help="Select one or more dessert options",
    )
    menu_meze_ids = fields.Many2many(
        'project.demo.menu.meze',
        'demo_form_meze_rel',
        'form_id',
        'meze_id',
        string="Appetizers (Meze)",
        help="Select one or more mezzes/appetizers",
    )
    menu_meze_notes=fields.Html(
        string="Menu Meze Notes",
        sanitize=True,
        help="Provide notes or instructions for the Menu page."
    )


    # ── Bar page ─────────────────────────────────────────────────────────────
    bar_description = fields.Html(
        string="Bar Notes",
        sanitize=True,
        help="Enter any instructions or notes for the bar setup."
    )
    bar_alcohol_service = fields.Boolean(
        string="Alcoholic Beverage Service",
        help="Does the bar include alcoholic beverages?"
    )
    bar_purchase_advice = fields.Char(
        string="If No, purchase advice",
        help="If no service, should guests purchase their own?"
    )
    bar_raki_brand = fields.Selection([
        ('mercan',             "Mercan"),
        ('beylerbeyi_gobek',   "Beylerbeyi Göbek"),
        ('tekirdag_altin_seri',"Tekirdağ Altın Seri"),
    ], string="Rakı Brand",
       help="Which brand of rakı will be served?")

    # ── After Party page ────────────────────────────────────────────────────
    afterparty_description = fields.Html(
        string="After Party Notes",
        sanitize=True,
        help="Notes or special instructions for the After Party."
    )
    afterparty_service = fields.Boolean(
        string="After Party",
        help="Do you want a dedicated After Party?"
    )
    afterparty_ultra = fields.Boolean(
        string="After Party Ultra",
        help="Include the Ultra After Party package?"
    )
    afterparty_more_drinks = fields.Boolean(
        string="Additional Drink Variety",
        help="Offer additional drink varieties?"
    )
    afterparty_street_food = fields.Boolean(
        string="Street Food",
        help="Include Street Food stations?"
    )
    afterparty_bbq_wraps = fields.Boolean(
        string="Barbeque Wraps",
        help="Include Barbeque Wraps?"
    )
    afterparty_sushi = fields.Boolean(
        string="Sushi",
        help="Include Sushi?"
    )
    afterparty_shot_service = fields.Boolean(
        string="Shot Service",
        help="Include a Shot Service?"
    )

    afterparty_dance_show = fields.Boolean(
        string="Dance Show",
        help="Include a dance performance?"
    )
    afterparty_fog_laser = fields.Boolean(
        string="Fog + Laser Show",
        help="Include fog and laser effects?"
    )

    additional_services_description = fields.Html(
        string="Additional Notes",
        sanitize=True,
    )

    prehost_barney = fields.Boolean(
        string="Barney",
        help="Include Pre‑Hosting by Barney?" )
    prehost_fred = fields.Boolean(
        string="Fred",
        help="Include Pre‑Hosting by Fred?" )
    prehost_breakfast = fields.Boolean(
        string="Breakfast Service",
        help="Include breakfast service?" )
    prehost_breakfast_count = fields.Integer(
        string="Breakfast Pax",
        help="If breakfast, how many people?" )
    prehost_notes=fields.Html(
        string="Prehost Notes",
        sanitize=True,
        help="Provide notes or instructions for the Menu page."
    )

    accommodation_hotel = fields.Char(
        string="Hotel",
        help="Name of the hotel for accommodation" )
    accommodation_service = fields.Boolean(
        string="Accommodation Provided",
        help="Is accommodation provided?" )

    accomodation_notes = fields.Html(
        string="Accomodation Notes",
        sanitize=True,
        help="Provide notes or instructions for the Menu page."
    )

    dance_lesson = fields.Boolean(
        string="Dance Lesson",
        help="Include a dance lesson?" )

    dance_lesson_notes = fields.Html(
        string="Dance Lesson Notes",
        sanitize=True,
        help="Provide notes or instructions for the Menu page."
    )

    hair_description = fields.Html(
        string="Hair & Makeup Notes", sanitize=True,
        help="Instructions or options for hair & makeup")
    hair_studio_3435 = fields.Boolean(
        string="Studio 3435 Nişantaşı")
    hair_garage_caddebostan = fields.Boolean(
        string="Garage Caddebostan")
    hair_other = fields.Boolean(string="Other")
    hair_other_company = fields.Char(string="Company")
    hair_other_responsible = fields.Char(string="Responsible")
    hair_other_phone = fields.Char(string="Phone")

    # Witnesses
    witness_description = fields.Html(
        string="Witnesses Notes", sanitize=True,
        help="List the witnesses (name & phone)")
    witness_line_ids = fields.One2many(
        'project.demo.witness.line', 'demo_form_id',
        string="Wedding Witnesses")

    # Photography
    photo_description = fields.Html(
        string="Photography Notes", sanitize=True)
    photo_standard = fields.Boolean(string="Standard Photo Service")
    photo_video_plus = fields.Boolean(string="Photo & Video Plus")
    photo_homesession = fields.Boolean(string="Home Session")
    photo_homesession_address = fields.Char(string="Address")
    photo_print_service = fields.Boolean(string="Photo Print Service")
    photo_drone = fields.Boolean(string="Drone Camera")
    photo_harddisk_delivered = fields.Boolean(string="Hard Disk 1 TB Delivered")
    photo_harddisk_later = fields.Boolean(string="Will Deliver Later")

    # Music
    music_description = fields.Html(
        string="Music Notes", sanitize=True)
    music_live = fields.Boolean(string="Live Music")
    music_trio = fields.Boolean(string="Trio")
    music_percussion = fields.Boolean(string="Percussion")
    music_dj_fatih = fields.Boolean(string="DJ: Fatih Aşçı")
    music_dj_engin = fields.Boolean(string="DJ: Engin Sadiki")
    music_other = fields.Boolean(string="Other")
    music_other_details = fields.Char(string="If Other, specify")

    # ── Table Decoration page ────────────────────────────────────────────────
    table_description = fields.Html(
        string="Table Decoration Notes",
        sanitize=True,
        help="Any notes for the table decoration"
    )
    table_theme = fields.Selection([
        ('rustic', "Rustic"),
        ('sea', "Sea"),
        ('garden', "Garden"),
        ('vintage', "Vintage"),
    ], string="Table Theme", )
    table_charger = fields.Selection([
        ('silver', "Silver"),
        ('wood', "Wood"),
        ('glass', "Glass"),
        ('wicker', "Wicker"),
    ], string="Charger Type", )
    table_runner_design = fields.Selection([
        ('center_horizontal', "Center Horizontal"),
        ('person_vertical', "Person-to-Person Vertical"),
    ], string="Cloth & Runner Design", )
    table_color = fields.Selection([
        ('white', "White"),
        ('turquoise', "Turquoise"),
        ('brown', "Brown"),
        ('blue', "Blue"),
        ('salmon', "Salmon"),
        ('beige', "Beige"),
        ('green', "Green"),
        ('terracotta', "Terracotta"),
        ('grey', "Grey"),
    ], string="Color Choice")
    table_tag = fields.Selection([
        ('romantic', "Romantic Tag"),
        ('rustic_tag', "Rustic Tag"),
        ('white_fairy', "White Fairy Tag"),
    ], string="Ceremony Tag")
    cake_choice = fields.Selection([
        ('green', "Green"),
        ('sea', "Sea"),
        ('purple', "Purple"),
        ('white_pink', "White & Pink"),
        ('real', "Real Cake"),
        ('champagne', "Champagne Tower"),
    ], string="Cake Choice")
    table_fresh_flowers = fields.Boolean(
        string="Fresh Flowers",
        help="Include fresh flowers?")
    table_dried_flowers = fields.Boolean(
        string="Dried Flowers",
        help="Include dried flowers?")

    # ── Other Notes page ──────────────────────────────────────────────────────
    other_description = fields.Html(
        string="Other Notes",
        sanitize=True,
        help="Any additional notes"
    )
    other_lcv = fields.Boolean(
        string="LCV",
        help="LCV required?")
    other_social_media_tag = fields.Boolean(
        string="Social Media Tag Me",
        help="Tag me on social media?")
    other_social_media_details = fields.Char(
        string="If Yes, details",
        help="Additional info for social media tagging")

    @api.model
    def create(self, vals):
        if 'name' in vals and vals.get('name') == _('New Demo Form'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'project.demo.form') or vals['name']
        return super().create(vals)




class DemoScheduleLine(models.Model):
    _name = 'project.demo.schedule.line'
    _description = "Demo Schedule Line"

    demo_form_id = fields.Many2one(
        'project.demo.form',  ondelete='cascade')
    sequence = fields.Integer(string="Step")
    event = fields.Char(string="Event")
    time = fields.Char(string="Time")
    location_type = fields.Selection(
        [('restaurant','Restaurant'),('beach','Beach')],
        string="Location Type")
    location_notes = fields.Char(string="Details")


class DemoTransportLine(models.Model):
    _name = 'project.demo.transport.line'
    _description = "Demo Transport Line"

    demo_form_id = fields.Many2one(
        'project.demo.form',  ondelete='cascade')
    sequence = fields.Integer(string="Step")
    label = fields.Char(string="Notes")
    time = fields.Char(string="Time",)
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
    phone = fields.Char(string="Phone")

class TransportPort(models.Model):
    _name = 'project.transport.port'
    _description = 'Transport Port'

    name = fields.Char(string="Port Name", required=True)

class DemoMenuDessert(models.Model):
    _name = 'project.demo.menu.dessert'
    _description = "Demo Menu Dessert Option"

    name = fields.Char(string="Dessert Name", required=True)

class DemoMenuMeze(models.Model):
    _name = 'project.demo.menu.meze'
    _description = "Demo Menu Appetizer (Meze)"

    name = fields.Char(string="Appetizer Name", required=True)