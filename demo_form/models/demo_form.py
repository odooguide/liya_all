from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError,RedirectWarning,UserError
from lxml import html as lhtml
from odoo.tools import html2plaintext, plaintext2html
import re
import json
from markupsafe import escape as E, Markup
import logging
from babel.dates import format_date
_logger = logging.getLogger(__name__)

TIME_PATTERN = re.compile(r'(\d{1,2}):([0-5]\d)')
TEMPLATE_INCLUDED_FIELDS = {
        'elite': {
            'afterparty_street_food',
        },
        'plus': {
            'photo_video_plus',
            'afterparty_service', 'afterparty_shot_service',
            'accommodation_service', 'dance_lesson',
            'afterparty_street_food',
        },
        'ultra': {
            'photo_video_plus',
            'afterparty_service', 'afterparty_shot_service',
            'accommodation_service', 'dance_lesson',
            'afterparty_street_food',
            'bar_alcohol_service', 'photo_drone',
            'afterparty_fog_laser', 'afterparty_bbq_wraps',
            'music_live', 'music_percussion', 'music_trio',
            'prehost_barney',

        },
    }



class ProjectDemoForm(models.Model):
    _name = 'project.demo.form'
    _description = "Project Demo Form"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sale_template_id = fields.Many2one('sale.order.template', string='Event Type')
    project_id = fields.Many2one(
        'project.project', string="Project", ondelete='cascade')
    name = fields.Char(
        string="Reference",
        default=lambda self: _('New Demo Form'))
    partner_id=fields.Many2one('res.partner',related='project_id.partner_id',string='Customer')
    invitation_owner = fields.Char(string="Invitation Owner")
    invitation_date = fields.Date(string="Invitation Date",)
    duration_days = fields.Char(string="Day", compute='_compute_day',translate=True)
    demo_date = fields.Date(string="Demo Date")
    special_notes = fields.Html(string="Special Notes")
    ceremony_call=fields.Boolean(string='Ceremony Call')

    wedding_type = fields.Selection([
        ('mini', "Mini Elite"),
        ('elite', "Elite"),
        ('plus', "Plus"),
        ('ultra', "Ultra")],
        string="Wedding Type")
    guest_count = fields.Integer(related='project_id.so_people_count',string="Guest Count")
    ceremony = fields.Selection([
        ('actual', "Official"),
        ('staged', "Non-Official")],
        string="Ceremony ")
    start_end_time = fields.Char(string="Start-End Time")

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
    menu_hot_appetizer_ultra = fields.Boolean(string='Rocket Shrimp')
    menu_dessert_ids = fields.Many2many(
        'project.demo.menu.dessert',
        'demo_form_dessert_rel',
        'form_id',
        'dessert_id',
        string="Dessert Choices",
        help="Select one or more dessert options",
    )
    menu_dessert_ultra_ids = fields.Many2many(
        'project.demo.menu.dessert.ultra',
        'demo_form_dessert_utlra_rel',
        'form_id',
        'dessert_id',
        string="Ultra Dessert Choices",
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
    menu_meze_notes = fields.Html(
        string="Menu Meze Notes",
        sanitize=True,
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
    alcohol_service=fields.Boolean(
        string="Alcohol Service",
        default=True
    )
    bar_purchase_advice = fields.Char(
        string="If No, purchase advice",
        help="If no service, should guests purchase their own?"
    )
    bar_raki_brand = fields.Selection([
        ('mercan', "Mercan"),
        ('beylerbeyi_gobek', "Beylerbeyi Göbek"),
        ('tekirdag_altin_seri', "Tekirdağ Altın Seri"),
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
        help="Do you want a dedicated After Party?", store=True,
    )
    afterparty_ultra = fields.Boolean(
        string="After Party Ultra",
        help="Include the Ultra After Party package?",
        store=True
    )
    afterparty_more_drinks = fields.Boolean(
        string="Additional Drink Variety",
        help="Offer additional drink varieties?"
    )
    afterparty_street_food = fields.Boolean(
        string="Street Food Atıştırmalık",
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
        help="Include a dance performance?",
        store=True,
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
        help="Include Pre‑Hosting by Barney?")
    prehost_fred = fields.Boolean(
        string="Fred",
        help="Include Pre‑Hosting by Fred?")
    prehost_breakfast = fields.Boolean(
        string="Breakfast Service",
        help="Include breakfast service?")
    prehost_breakfast_count = fields.Integer(
        string="Breakfast Pax",
        help="If breakfast, how many people?")
    prehost_notes = fields.Html(
        string="Prehost Notes",
        sanitize=True,
        help="Provide notes or instructions for the Menu page."
    )

    accommodation_hotel = fields.Char(
        string="Hotel",
        help="Name of the hotel for accommodation")
    accommodation_service = fields.Boolean(
        string="Accommodation",
        help="Is accommodation provided?")

    accomodation_notes = fields.Html(
        string="Accomodation Notes",
        sanitize=True,
        help="Provide notes or instructions for the Menu page."
    )

    dance_lesson = fields.Boolean(
        string="Dance Lesson",
        help="Include a dance lesson?")

    dance_lesson_notes = fields.Html(
        string="Dance Lesson Notes",
        sanitize=True,
        help="Provide notes or instructions for the Menu page."
    )

    hair_description = fields.Html(
        string="Hair & Makeup Notes", sanitize=True,
        help="Instructions or options for hair & makeup")
    hair_studio_3435 = fields.Boolean(string="Studio 3435 Nişantaşı")
    hair_garage_caddebostan = fields.Boolean(string="Garage Caddebostan")
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
    photo_description = fields.Html(string="Photography Notes", sanitize=True)
    photo_standard = fields.Boolean(string="Standard Photo Service")
    photo_video_plus = fields.Boolean(string="Photo & Video Plus")
    #photo_homesession = fields.Boolean(string="Home Session")
    photo_homesession_address = fields.Char(string="Address")
    photo_print_service = fields.Boolean(string="Photo Print Service")
    photo_drone = fields.Boolean(string="Drone Camera")
    photo_harddisk_delivered = fields.Selection(
        [('delivered', 'Delivered'),
         ('later', 'Deliver Later')],
        string="Hard Disk 1TB")
    photo_yacht_shoot = fields.Boolean(string='Yacht Photo Shoot')
    # Music
    music_description = fields.Html(
        string="Music Notes", sanitize=True)
    music_live = fields.Boolean(string="Live Music")
    music_trio = fields.Boolean(string="Trio")
    music_percussion = fields.Boolean(string="Percussion")
    music_other = fields.Boolean(string="Other")
    dj_person = fields.Selection([('engin', 'Engin Sadiki'), ('fatih', 'Fatih Aşçı'), ('other', 'Diğer')],
                                 string='DJ')
    music_other_details = fields.Char(string="If Other, specify")

    # ── Table Decoration page ────────────────────────────────────────────────
    table_description = fields.Html(
        string="Table Decoration Notes",
        sanitize=True,
        help="Any notes for the table decoration"
    )
    table_theme_ids = fields.Many2many(
        'project.demo.table.theme',
        'rel_form_table_theme',  # relation table
        'demo_form_id', 'theme_id',  # fkeys
        string="Table Themes")

    table_charger_ids = fields.Many2many(
        'project.demo.table.charger',
        'rel_form_table_charger',
        'demo_form_id', 'charger_id',
        string="Charger Types")

    table_runner_design_ids = fields.Many2many(
        'project.demo.runner.design',
        'rel_form_runner_design',
        'demo_form_id', 'runner_id',
        string="Cloth & Runner Designs")

    table_color_ids = fields.Many2many(
        'project.demo.table.color',
        'rel_form_table_color',
        'demo_form_id', 'color_id',
        string="Color Choices")

    table_tag_ids = fields.Many2one(
        'project.demo.ceremony.tag',

        string="Ceremony Tags")

    cake_choice_ids = fields.Many2many(
        'project.demo.cake.choice',
        'rel_form_cake_choice',
        'demo_form_id', 'cake_id',
        string="Cake Choices")
    cake_real = fields.Boolean(string='Real Cake')
    cake_champagne_tower = fields.Boolean(string='Champagne Tower')
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
    # ── 1. Significant Songs ────────────────────────────────────────────────
    entrance_song = fields.Char(string="Entrance Song")
    first_dance_song = fields.Char(string="First Dance Song")
    cake_song = fields.Char(string="Wedding Cake Song")
    bouquet_toss_song = fields.Char(string="Bouquet Toss Song")

    # ── 2A. Language Ratio ─────────────────────────────────────────────────
    ratio_choice = fields.Selection([
        ('50_50', "Turkish 50 / Foreign 50"),
        ('25_75', "Turkish 25 / Foreign 75"),
        ('75_25', "Turkish 75 / Foreign 25"),
        ('other', "Other"),
    ], string="Language Ratio", default='50_50')
    ratio_turkish = fields.Integer(string="Turkish %")
    ratio_foreign = fields.Integer(string="Foreign %")

    # ── 2B. Type of Music ── Cocktail ──────────────────────────────────────
    cocktail_lounge = fields.Boolean(string="Lounge")
    cocktail_french = fields.Boolean(string="French")
    cocktail_italian = fields.Boolean(string="Italian")
    cocktail_greek = fields.Boolean(string="Greek")
    cocktail_house = fields.Boolean(string="House")
    cocktail_easy_bossa = fields.Boolean(string="Easy Listening & Bossa")

    # ── Dinner ─────────────────────────────────────────────────────────────
    dinner_lounge = fields.Boolean(string="Lounge")
    dinner_turkish_acoustic = fields.Boolean(string="Turkish Acoustic")
    dinner_turkish_retro = fields.Boolean(string="Turkish Retro")
    dinner_italian_french_greek = fields.Boolean(string="Italian & French & Greek")
    dinner_oldies = fields.Boolean(string="Oldies & Goldies")

    # ── Party ──────────────────────────────────────────────────────────────
    party_turkish = fields.Boolean(string="Turkish")
    party_turkish_80s_90s = fields.Boolean(string="Turkish 80’s 90’s")
    party_local = fields.Boolean(string="Yöresel / Local")
    party_radio_top50 = fields.Boolean(string="Radio Top 50")
    party_oldies = fields.Boolean(string="Oldies & Goldies")
    party_latin_salsa = fields.Boolean(string="Latin & Salsa & Reggaeton")
    party_hiphop_rnb = fields.Boolean(string="Hip Hop & R&B")
    party_90s_2000s_hits = fields.Boolean(string="90’s 2000’s Hits")
    party_turkish_rock = fields.Boolean(string="Turkish Rock")
    party_house_electronic = fields.Boolean(string="House & Electronic")

    # ── After Party ────────────────────────────────────────────────────────
    after_turkish = fields.Boolean(string="Turkish")
    after_turkish_80s_90s = fields.Boolean(string="Turkish 80’s 90’s")
    after_radio_top50 = fields.Boolean(string="Radio Top 50")
    after_party_hits = fields.Boolean(string="Party Hits")
    after_oldies = fields.Boolean(string="Oldies & Goldies")
    after_latin_salsa = fields.Boolean(string="Latin & Salsa & Reggaeton")
    after_hiphop_rnb = fields.Boolean(string="Hip Hop & R&B")
    after_90s_2000s_hits = fields.Boolean(string="90’s 2000’s Hits")
    after_turkish_rock = fields.Boolean(string="Turkish Rock")
    after_house_electronic = fields.Boolean(string="House & Electronic")
    confirmed_demo_form_plan = fields.Binary(string="Confirmed Demo Form")
    confirmed_demo_form_plan_name = fields.Char(string="Confirmed Demo Form Name")
    local_music = fields.Boolean(string="Local Music during Party")
    local_music_songs = fields.Html(string="If yes, specify songs")
    cocktail_request = fields.Html(string="Cocktail Request Musics", sanitize=True)
    dinner_request = fields.Html(string="Dinner Request Musics", sanitize=True)
    party_request = fields.Html(string="Party Request Musics", sanitize=True)
    afterparty_request = fields.Html(string="Afterparty Request Musics", sanitize=True)
    ban_songs = fields.Html(string="Ban any Songs or Artists", sanitize=True)
    other_music_notes = fields.Html(string="Other Notes about Music", sanitize=True)
    special_notes_preview = fields.Html(string="Special Notes Preview", compute='_compute_split_notes')
    special_notes_remaining = fields.Html(string="Special Notes Remaining", compute='_compute_split_notes')

    is_ceremony=fields.Boolean(string="Seramoni Düzeni")
    merasim=fields.Selection([('nostaljik','Beach'),('yemek','Restaurant'),('none','None')],string='Presents Accepting Area')

    demo_part_ids = fields.Many2many(
        'demo.form.print',
        'rel_form_demo_print',  # relation table
        'demo_form_id', 'demo_print_id',  # fkeys
        string="Demo Parts")

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )
    minutes = fields.Integer(string='Adjust Time')
    demo_seat_plan=fields.Many2one('demo.seat.plan', string='Oturma Planı')
    home_exit=fields.Boolean(string='Ev Çıkış Fotoğraf Çekimi')
    lang=fields.Selection([('tr_TR','Türkçe'),('en_US','English')],default='tr_TR')
    wedding_trio_ids = fields.One2many(
        'wedding.trio', 'project_id', string='Wedding Trios',
        compute='_mirror_wedding_trio', store=False, readonly=True)
    blue_marmara_ids = fields.One2many(
        'blue.marmara', 'project_id', string='Blue Marmara',
        compute='_mirror_blue_marmara', store=False, readonly=True)
    studio_345 = fields.One2many(
        'studio.345', 'project_id', string='Studio 3435',
        compute='_mirror_studio_345', store=False, readonly=True)
    garage_caddebostan = fields.One2many(
        'garage.caddebostan', 'project_id', string='Garage Caddebostan',
        compute='_mirror_garage_caddebostan', store=False, readonly=True)
    vedan_ids = fields.One2many(
        'partner.vedans', 'project_id', string='Partner Vedans',
        compute='_mirror_partner_vedans', store=False, readonly=True)
    live_music_ids = fields.One2many(
        'live.music', 'project_id', string='Live Music',
        compute='_mirror_live_music', store=False, readonly=True)
    backlight_ids = fields.One2many(
        'backlight', 'project_id', string='Backlight',
        compute='_mirror_backlight', store=False, readonly=True)
    confirmed_demo_ids = fields.One2many(
        comodel_name='confirmed.form',
        inverse_name='project_id',
        string='Confirmed Demo Forms',
        compute='_compute_confirmed_demo_form_ids',
        readonly=True,
        store=True,
    )
    demo_menu_ids = fields.One2many(
        comodel_name='demo.menu',
        inverse_name='project_id',
        string='Demo Menu',
        compute='_compute_demo_menu_ids',
        readonly=True,
        store=True,
    )

    PRODUCT_REQUIREMENTS = {
        'photo_video_plus': ['Photo & Video Plus'],
        'photo_drone': ['Drone Kamera'],
        'afterparty_service': ['After Party'],
        'afterparty_ultra': ['After Party Ultra'],
        'afterparty_shot_service': ['After Party Shot Servisi'],
        'afterparty_sushi': ['Sushi Bar'],
        'afterparty_dance_show': ['Dans Show'],
        'afterparty_fog_laser': ['Fog + Laser Show'],
        'bar_alcohol_service': ['Yabancı İçki Servisi'],
        'hair_studio_3435': ['Saç & Makyaj'],
        'hair_garage_caddebostan': ['Saç & Makyaj'],
        "cake_real": ["Pasta Show'da Gerçek Pasta"],
        "cake_champagne_tower": ["Pasta Show'da Şampanya Kulesi"],
        'prehost_barney': ['BARNEY'],
        'prehost_fred': ['FRED'],
        'accommodation_service': ['Konaklama'],
        'dance_lesson': ['Dans Dersi'],
        'prehost_breakfast': ['Kahvaltı'],
        'home_exit': ['Ev Çıkış Fotoğraf Çekimi'],
        'music_live': ['Canlı Müzik'],
        'music_trio': ['Trio'],
        'music_percussion': ['Perküsyon'],
    }
    TRACKED_FIELDS = list(PRODUCT_REQUIREMENTS.keys())

    @api.depends(
        'transport_line_ids',
        'transport_line_ids.label',
        'transport_line_ids.time',
        'transport_line_ids.port_ids',
        'project_id',
        'project_id.event_date',
    )
    def _compute_wedding_trio_ids(self):
        for rec in self:
            commands = [(5, 0, 0)]
            if not rec.music_trio:
                rec.wedding_trio_ids = commands
                continue
            event_date = (
                getattr(rec.project_id, 'event_date', False)
            )

            gg_lines = rec.transport_line_ids.filtered(
                lambda l: (l.label or '').strip().lower() == 'genel geliş'
            )
            for line in gg_lines:
                commands.append((
                    0, 0, {
                    'name': line.label or 'Genel Geliş',
                    'time': line.time,
                    'date': event_date,
                    'port_ids': [(6, 0, line.port_ids.ids)],
                }
                ))
            rec.wedding_trio_ids = commands

    @api.depends(
        'invitation_owner',
        'guest_count',  # related alan olsa da ekledik
        'project_id',
        'project_id.so_people_count',  # güvence için kaynağı da dinliyoruz
        'project_id.event_date',  # etkinlik tarihi alanın buysa
    )
    def _compute_blue_marmara_ids(self):
        for rec in self:
            event_date = (
                    getattr(rec.project_id, 'event_date', False)
                    or getattr(rec.project_id, 'date_start', False)
                    or getattr(rec.project_id, 'date', False)
            )
            if event_date:
                event_date = fields.Date.to_date(event_date)

            gc = rec.guest_count or 0
            boat = '36m' if gc > 250 else '25m'

            name_val = (rec.invitation_owner or 'Blue Marmara').strip()

            rec.blue_marmara_ids = [
                (5, 0, 0),
                (0, 0, {
                    'name': name_val,
                    'guest_count': str(gc),
                    'date': event_date,
                    'boat': boat,
                })
            ]

    @api.depends(
        'hair_studio_3435',  # yalnızca Studio 3435 seçildiyse satır üret
        'invitation_owner',
        'invitation_date', 'demo_date',
        'project_id',
        'project_id.reinvoiced_sale_order_id',
        'project_id.reinvoiced_sale_order_id.opportunity_id',
        'project_id.reinvoiced_sale_order_id.partner_id',
    )
    def _compute_studio_345(self):
        for rec in self:
            # önce temizle
            cmds = [(5, 0, 0)]

            # Studio 3435 seçili değilse hiç satır üretme
            if not rec.hair_studio_3435:
                rec.studio_345 = cmds
                continue

            # Etkinlik tarihi: davetiye > demo > (gerekirse proje alanları)
            event_date = rec.invitation_date or rec.demo_date
            if not event_date and rec.project_id:
                # varsa muhtemel proje tarih alanları
                event_date = (
                        getattr(rec.project_id, 'event_date', False)
                        or getattr(rec.project_id, 'date_start', False)
                        or getattr(rec.project_id, 'date', False)
                )
            if event_date:
                event_date = fields.Date.to_date(event_date)

            order = rec.project_id.sudo().reinvoiced_sale_order_id if rec.project_id else False
            opp = order.sudo().opportunity_id if order else False
            partner = order.sudo().partner_id if order else False

            couple = (opp.name or '').strip() if opp else ''
            # 1. telefon: partner.mobile > partner.phone > opp.mobile > opp.phone
            first_name = ''
            second_name = ''
            first_phone = ''
            if partner:
                first_phone = (partner.mobile or partner.phone or '') or ''
                first_name = partner.name or ''
            if not first_phone and opp:
                first_phone = (getattr(opp, 'mobile', '') or getattr(opp, 'phone', '') or '')

            # 2. telefon: olası özel alanlar
            second_phone = ''
            if opp:
                for attr in ('second_phone', 'second_contact_phone', 'x_second_phone', 'x_phone2'):
                    val = getattr(opp, attr, '') or ''
                    if val:
                        second_phone = val
                        break
                second_name = opp.second_contact

            # Satır adı: davet sahibi varsa onu, yoksa "Çift - Studio 3435"
            name_val = (rec.invitation_owner or '').strip()
            if not name_val:
                bits = [b for b in [couple, "Studio 3435 Nişantaşı"] if b]
                name_val = " - ".join(bits) or "Studio 3435"

            # Studio adı sabit
            studio_name = "Studio 3435 Nişantaşı"

            cmds.append((0, 0, {
                'name': name_val,
                'date': event_date,
                'opportunity_name': couple,
                'first_name': first_name,
                'second_name': second_name,
                'first_phone': first_phone,
                'second_phone': second_phone,
                'photo_studio': studio_name,
                'project_id': rec.id,
            }))

            rec.studio_345 = cmds

    @api.depends(
        'hair_garage_caddebostan',  # yalnızca Studio 3435 seçildiyse satır üret
        'invitation_owner',
        'invitation_date', 'demo_date',
        'project_id',
        'project_id.reinvoiced_sale_order_id',
        'project_id.reinvoiced_sale_order_id.opportunity_id',
        'project_id.reinvoiced_sale_order_id.partner_id',
    )
    def _compute_garage_caddebostan(self):
        for rec in self:
            cmds = [(5, 0, 0)]

            if not rec.hair_garage_caddebostan:
                rec.garage_caddebostan = cmds
                continue

            event_date = rec.invitation_date or rec.demo_date
            if not event_date and rec.project_id:
                event_date = (
                        getattr(rec.project_id, 'event_date', False)
                        or getattr(rec.project_id, 'date_start', False)
                        or getattr(rec.project_id, 'date', False)
                )
            if event_date:
                event_date = fields.Date.to_date(event_date)

            # CRM fırsat + partner bilgileri (sudo ile güvenli)
            order = rec.project_id.sudo().reinvoiced_sale_order_id if rec.project_id else False
            opp = order.sudo().opportunity_id if order else False
            partner = order.sudo().partner_id if order else False

            couple = (opp.name or '').strip() if opp else ''
            first_name = ''
            second_name = ''
            first_phone = ''
            if partner:
                first_phone = (partner.mobile or partner.phone or '') or ''
                first_name = partner.name or ''
            if not first_phone and opp:
                first_phone = (getattr(opp, 'mobile', '') or getattr(opp, 'phone', '') or '')

            # 2. telefon: olası özel alanlar
            second_phone = ''
            if opp:
                for attr in ('second_phone', 'second_contact_phone', 'x_second_phone', 'x_phone2'):
                    val = getattr(opp, attr, '') or ''
                    if val:
                        second_phone = val
                        break
                second_name = opp.second_contact

            name_val = (rec.invitation_owner or '').strip()
            if not name_val:
                bits = [b for b in [couple, "Garage Caddebostan"] if b]
                name_val = " - ".join(bits) or "Garage Caddebostan"

            studio_name = "Garage Caddebostan"

            cmds.append((0, 0, {
                'name': name_val,
                'date': event_date,
                'opportunity_name': couple,
                'first_name': first_name,
                'second_name': second_name,
                'first_phone': first_phone,
                'second_phone': second_phone,
                'photo_studio': studio_name,
                'project_id': rec.id,
            }))

            rec.garage_caddebostan = cmds

    @api.depends(
        'invitation_owner',
        'invitation_date', 'demo_date',
        'project_id',
        'project_id.reinvoiced_sale_order_id',
        'project_id.reinvoiced_sale_order_id.opportunity_id',
        'project_id.reinvoiced_sale_order_id.partner_id',
    )
    def _compute_partner_vedan(self):
        for rec in self:
            cmds = [(5, 0, 0)]

            event_date = rec.invitation_date or rec.demo_date
            if not event_date and rec.project_id:
                event_date = (
                        getattr(rec.project_id, 'event_date', False)
                        or getattr(rec.project_id, 'date_start', False)
                        or getattr(rec.project_id, 'date', False)
                )
            if event_date:
                event_date = fields.Date.to_date(event_date)

            order = rec.project_id.sudo().reinvoiced_sale_order_id if rec.project_id else False
            opp = order.sudo().opportunity_id if order else False
            partner = order.sudo().partner_id if order else False

            couple = (opp.name or '').strip() if opp else ''
            first_name = ''
            second_name = ''
            first_phone = ''
            if partner:
                first_phone = (partner.mobile or partner.phone or '') or ''
                first_name = partner.name or ''
            if not first_phone and opp:
                first_phone = (getattr(opp, 'mobile', '') or getattr(opp, 'phone', '') or '')

            # 2. telefon: olası özel alanlar
            second_phone = ''
            if opp:
                for attr in ('second_phone', 'second_contact_phone', 'x_second_phone', 'x_phone2'):
                    val = getattr(opp, attr, '') or ''
                    if val:
                        second_phone = val
                        break
                second_name = opp.second_contact

            name_val = (rec.invitation_owner or '').strip()

            cmds.append((0, 0, {
                'name': name_val,
                'date': event_date,
                'opportunity_name': couple,
                'first_name': first_name,
                'second_name': second_name,
                'first_phone': first_phone,
                'second_phone': second_phone,
                'project_id': rec.id,
            }))

            rec.vedan_ids = cmds

    @api.depends(
        'demo_date',
        'sale_template_id'
    )
    def _compute_live_music(self):
        for rec in self:
            cmds = [(5, 0, 0)]
            if not rec.music_live:
                rec.live_music_ids = cmds
                continue
            event_date = rec.invitation_date or rec.demo_date
            if not event_date and rec.project_id:
                event_date = (
                        getattr(rec.project_id, 'event_date', False)
                        or getattr(rec.project_id, 'date_start', False)
                        or getattr(rec.project_id, 'date', False)
                )
            if event_date:
                event_date = fields.Date.to_date(event_date)

            tmpl_name = self.sudo().sale_template_id.name or ''

            cmds.append((0, 0, {
                'name': tmpl_name,
                'date': event_date,
                'project_id': rec.id,
            }))

            rec.live_music_ids = cmds

    @api.depends(
        'photo_drone', 'home_exit',
        'invitation_owner',
        'invitation_date', 'demo_date',
        'project_id',
        'project_id.event_date',
        'project_id.so_opportunity_id',
        'project_id.so_opportunity_id.name',
        'project_id.so_opportunity_id.phone',
        'project_id.so_opportunity_id.second_phone',
        'project_id.email_from',  # birincil mail (istersen opp.email_from'a da çekebilirsin)
        'project_id.so_opportunity_id.second_mail',  # İKİNCİL mail → OPP üzerinden
    )
    def _compute_backlight_ids(self):
        for rec in self:
            cmds = [(5, 0, 0)]

            event_date = rec.invitation_date or rec.demo_date or rec.project_id.event_date
            if event_date:
                event_date = fields.Date.to_date(event_date)

            order = rec.project_id.sudo().reinvoiced_sale_order_id if rec.project_id else False
            opp = order.sudo().opportunity_id if order else False
            partner = order.sudo().partner_id if order else False
            couple_name = (opp.name or '').strip() if opp else ''
            first_name = ''
            second_name = ''
            first_phone = ''
            if partner:
                first_phone = (partner.mobile or partner.phone or '') or ''
                first_name = partner.name or ''
            if not first_phone and opp:
                first_phone = (getattr(opp, 'mobile', '') or getattr(opp, 'phone', '') or '')

            # 2. telefon: olası özel alanlar
            second_phone = ''
            if opp:
                for attr in ('second_phone', 'second_contact_phone', 'x_second_phone', 'x_phone2'):
                    val = getattr(opp, attr, '') or ''
                    if val:
                        second_phone = val
                        break
                second_name = opp.second_contact

            # MAİLLER
            first_mail = (rec.project_id.email_from or '').strip()  # birincil mail (proje related)
            second_mail = (getattr(opp, 'second_mail', '') or '').strip() if opp else ''  # İKİNCİL mail → OPP

            drone_str = "Var" if getattr(rec, 'photo_drone', False) else "Yok"
            home_exit_str = "Var" if getattr(rec, 'home_exit', False) else "Yok"

            name_val = (rec.invitation_owner or '').strip()
            if not name_val:
                bits = [b for b in [couple_name, "Backlight"] if b]
                name_val = " - ".join(bits) or "Backlight"

            if rec.photo_standard:
                photo_service = 'Standart Fotoğraf Servisi'
            elif rec.photo_video_plus:
                photo_service = 'Photo & Video Plus'
            else:
                photo_service = ''

            sale_template_name = rec.sale_template_id.name or ''

            yacht_shoot = 'VAR' if rec.photo_yacht_shoot else 'YOK'
            photo_print_service = 'VAR' if rec.photo_print_service else 'YOK'

            cmds.append((0, 0, {
                'name': name_val,
                'date': event_date,
                'opportunity_name': couple_name,
                'first_name': first_name,
                'second_name': second_name,
                'first_phone': first_phone,
                'second_phone': second_phone,
                'project_id': rec.id,
                'first_mail': first_mail,
                'second_mail': second_mail,
                'drone': drone_str,
                'home_exit': home_exit_str,
                'photo_service': photo_service,
                'sale_template_name': sale_template_name,
                'yacht_shoot': yacht_shoot,
                'photo_print_service': photo_print_service,
            }))

            rec.backlight_ids = cmds

    @api.depends(
        'project_id',
        'confirmed_demo_form_plan',
        'invitation_date'
    )
    def _compute_confirmed_demo_form_ids(self):
        for rec in self:
            cmds=[(5,0,0)]
            payload = rec.with_context(bin_size=False).confirmed_demo_form_plan
            if not payload:
                rec.confirmed_demo_ids=cmds
                continue

            event_date = rec.invitation_date or rec.demo_date or rec.project_id.event_date
            if event_date:
                event_date = fields.Date.to_date(event_date)
            name=rec.invitation_owner or ''
            form_name=rec.confirmed_demo_form_plan_name or ''

            cmds.append((0, 0, {
                'name': name,
                'date': event_date,
                'project_id': rec.id,
                'confirmed_demo_form':payload,
                'form_name':form_name,
            }))
            rec.confirmed_demo_ids=cmds


    @api.depends(
        'invitation_owner', 'invitation_date', 'demo_date',
        'project_id', 'project_id.event_date',
        'menu_description',
        'menu_hot_appetizer', 'menu_hot_appetizer_ultra',
        'menu_dessert_ids', 'menu_dessert_ultra_ids',
        'menu_meze_ids', 'menu_meze_notes',
        'afterparty_street_food', 'afterparty_bbq_wraps', 'afterparty_sushi',
    )
    def _compute_demo_menu_ids(self):
        def to_text(rec, html):
            """HTML alanlarını düz metne çevir (sende zaten _html_to_text varsa onu kullan)."""
            if not html:
                return ""
            if hasattr(rec, '_html_to_text'):
                return rec._html_to_text(html)
            import re
            return re.sub(r'<[^>]+>', '', html or '').strip()

        for rec in self:
            commands = [(5, 0, 0)]

            # tarih: davetiye > demo > proje
            event_date = rec.invitation_date or rec.demo_date or getattr(rec.project_id, 'event_date', False)
            if event_date:
                event_date = fields.Date.to_date(event_date)

            # başlık
            name_val = (rec.invitation_owner or 'Demo Menü').strip()

            hot_label = ""
            try:
                hot_map = dict(rec._fields['menu_hot_appetizer']._description_selection(rec.env))
                hot_label = hot_map.get(rec.menu_hot_appetizer, "") if rec.menu_hot_appetizer else ""
            except Exception:
                hot_label = rec.menu_hot_appetizer or ""

            def names(m2m):
                return ", ".join(m2m.mapped('name')) if m2m else ""

            lines = []
            lines.append(f'➖ Kişi Sayısı: {rec.guest_count}px')

            if hot_label:
                lines.append(f"➖ Sıcak Başlangıç: {hot_label}")
            if rec.menu_hot_appetizer_ultra:
                lines.append("➖ Sıcak Ekstra: Rocket Shrimp")

            meze_txt = names(rec.menu_meze_ids)
            if meze_txt:
                lines.append(f"➖ Mezeler: {meze_txt}")

            meze_note_txt = to_text(rec, rec.menu_meze_notes)
            if meze_note_txt:
                lines.append(f"➖ Meze Notu: {meze_note_txt}")

            dessert_txt = names(rec.menu_dessert_ids)
            if dessert_txt:
                lines.append(f"➖ Tatlı: {dessert_txt}")

            dessert_ultra_txt = names(rec.menu_dessert_ultra_ids)
            if dessert_ultra_txt:
                lines.append(f"➖ Ultra Tatlı: {dessert_ultra_txt}")

            af_bits = []
            if rec.afterparty_sushi:
                af_bits.append("Sushi")
            if rec.afterparty_street_food:
                af_bits.append("Street Food Atıştırmalık")
            if rec.afterparty_bbq_wraps:
                af_bits.append("Barbeque Wraps")
            if af_bits:
                lines.append("➖ After Party: " + ", ".join(af_bits))
            if rec.prehost_breakfast:
                lines.append(f'➖ Kahvaltı: {rec.prehost_breakfast_count}px')
            menu_note_txt = to_text(rec, rec.menu_description)
            if menu_note_txt:
                if lines:
                    lines.append("")
                lines.append(menu_note_txt)



            menu_notes = "\n".join(lines).strip()


            if menu_notes or name_val or event_date:
                commands.append((0, 0, {
                    'name': name_val,
                    'date': event_date,
                    'project_id': rec.id,
                    'menu_info': menu_notes,
                }))

            rec.demo_menu_ids = commands

    @api.model
    def cron_recompute_all_compute_fields(self, batch_size=500):
        """
        Tüm project.demo.form kayıtları için ilgili compute fonksiyonlarını çağırır.
        Büyük setlerde bellek kullanımını azaltmak için batch ile ilerler.
        """

        DemoForm = self.env["project.demo.form"].sudo()
        domain = []

        ids = DemoForm.search(domain).ids
        total = len(ids)
        _logger.info("[Cron] project.demo.form compute taraması başlıyor. Kayıt sayısı: %s", total)

        for start in range(0, total, batch_size):
            chunk_ids = ids[start:start + batch_size]
            recs = DemoForm.browse(chunk_ids)
            try:
                recs._compute_wedding_trio_ids()
                recs._compute_blue_marmara_ids()
                recs._compute_studio_345()
                recs._compute_garage_caddebostan()
                recs._compute_partner_vedan()
                recs._compute_live_music()
                recs._compute_backlight_ids()

                # İsteğe bağlı: cache temizliği
                recs.invalidate_cache()
            except Exception:
                _logger.exception(
                    "[Cron] Compute çağrısı sırasında hata oluştu (ids: %s)", chunk_ids
                )

        _logger.info("[Cron] project.demo.form compute taraması tamamlandı. Toplam: %s", total)

    @api.onchange('confirmed_demo_form_plan')
    def _onchange_confirmed_contract_security(self):
        for rec in self:
            origin = rec._origin
            if origin.confirmed_demo_form_plan and not self.env.user.has_group('base.group_system'):
                rec.confirmed_demo_form_plan = origin.confirmed_demo_form_plan
                raise UserError(
                    _('Only administrators can modify or delete the Confirmed Demo Form once uploaded.')
                )

    def _template_key(self):
        name = (self.sudo().sale_template_id.name or '').strip().lower()
        if not name and self.project_id and self.project_id.reinvoiced_sale_order_id:
            name = (self.project_id.sudo().reinvoiced_sale_order_id.sale_order_template_id.name or '').strip().lower()
        if 'elite' in name:
            return 'elite'
        if 'plus' in name:
            return 'plus'
        if 'ultra' in name:
            return 'ultra'
        return None

    def _template_included_fields(self):
        key = self._template_key()
        return TEMPLATE_INCLUDED_FIELDS.get(key, set())

    def _template_included_labels(self):
        """Şablonun dahil ettiği field’lardan beklenen ürün etiketlerini üretir."""
        labels = set()
        for f in self._template_included_fields():
            for lbl in self._required_labels_for_field(f):
                if lbl:
                    labels.add(lbl)
        return labels

    def _get_related_confirmed_sale_orders(self):
        """Bu projenin M2M 'Bağlı Satışlar'ındaki TÜM siparişler (durum süzmeden)."""
        self.ensure_one()
        project = self.project_id
        if not project:
            return self.env['sale.order']
        return project.sudo().related_sale_order_ids

    def _required_labels_for_field(self, field_name):
        """Bir alan için beklenen ürün etiket(ler)i; seçim alanı için prospective_val kullanılabilir."""
        mapping = self.PRODUCT_REQUIREMENTS.get(field_name)
        if not mapping:
            return []
        return mapping

    @api.depends('special_notes')
    def _compute_split_notes(self):
        import re

        def _smart_join_breaks(html: str, punct=',.'):
            # 1) HTML kırıcılarını yer tutucuya çevir
            html = re.sub(r'(<\s*br\s*/?\s*>|</\s*(?:p|div|li|tr|h[1-6])\s*>)',
                          '[[BR]]', html, flags=re.I)
            html = re.sub(r'(\s*\[\[BR\]\]\s*)+', '[[BR]]', html)

            # 2) Etrafında noktalama varsa -> sadece boşluk
            html = re.sub(rf'([{re.escape(punct)}])\s*\[\[BR\]\]\s*', r'\1 ', html)  # önce varsa
            html = re.sub(rf'\s*\[\[BR\]\]\s*([{re.escape(punct)}])', r' \1', html)  # sonra varsa

            # 3) Kalan kırıcılar -> ", "
            html = re.sub(r'\s*\[\[BR\]\]\s*', ', ', html)

            # 4) Temizlik
            html = re.sub(r'[ \t\u00A0]+', ' ', html)
            html = re.sub(r'\s+,', ', ', html)
            html = re.sub(r'(,\s*){2,}', ', ', html)
            return html.strip(' ,')

        limit = 300
        for rec in self:
            raw_html = rec.special_notes or ''

            # HTML seviyesinde akıllı birleştirme (yalnızca virgül/nokta kuralı)
            prepped_html = _smart_join_breaks(raw_html, punct=',.')

            # Plain text'e çevir
            notes = html2plaintext(prepped_html or '')

            notes = notes.replace('\r\n', '\n').replace('\r', '\n')
            notes = re.sub(r'[ \t\u00A0]+', ' ', notes)
            notes = re.sub(r'\s*\n+\s*', ' ', notes)
            notes = re.sub(r'\s{2,}', ' ', notes).strip()

            if len(notes) <= limit:
                preview, remaining = notes, ''
            else:
                cut = notes[:limit]
                last_break = max(cut.rfind(', '), cut.rfind(' '))
                split_at = last_break if last_break != -1 else limit
                preview = cut[:split_at]
                remaining = notes[split_at:].lstrip()

            rec.special_notes_preview = plaintext2html(preview)
            rec.special_notes_remaining = plaintext2html(remaining) if remaining else ''

    @api.depends('invitation_date', 'lang')
    def _compute_day(self):
        tr_days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        en_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        for rec in self:
            if not rec.invitation_date:
                rec.duration_days = False
                continue

            dt = fields.Date.to_date(rec.invitation_date)

            try:
                locale = rec.lang or 'tr_TR'
                rec.duration_days = format_date(dt, format='EEEE', locale=locale)
            except Exception:
                # Yedek: basit dizi eşlemesi
                idx = dt.weekday()  # 0=Monday .. 6=Sunday
                rec.duration_days = (tr_days if rec.lang == 'tr_TR' else en_days)[idx]

    @api.onchange('afterparty_ultra')
    def _onchange_afterparty_ultra_open(self):
        if self.afterparty_ultra:
            self.afterparty_fog_laser = True
            self.afterparty_street_food = False
            self.afterparty_bbq_wraps = True
            self.afterparty_shot_service = True
        else:
            self.afterparty_fog_laser = False
            self.afterparty_bbq_wraps = False
            self.afterparty_shot_service = False

    @api.onchange('afterparty_service')
    def _onchange_afterparty_service_open(self):
        if self.afterparty_service:
            self.afterparty_street_food = True
        else:
            self.afterparty_street_food = False


    def _onchange_start_end_time(self):
        for rec in self:
            if rec.afterparty_ultra:
                base_end_dt = datetime.strptime('02:00', '%H:%M')
            elif rec.afterparty_service:
                base_end_dt = datetime.strptime('01:30', '%H:%M')
            else:
                base_end_dt = datetime.strptime('23:30', '%H:%M')

            end_str = base_end_dt.strftime('%H:%M')

            rec.start_end_time = f'19:30-{end_str}'

            for line in rec.schedule_line_ids.filtered(lambda l: l.event in ['After Party','After Parti']):
                if rec.afterparty_ultra or rec.afterparty_service:
                    line.time = f'23:30 - {end_str}'
                else:
                    line.time = ''


            party_end_dt = datetime.strptime('23:30', '%H:%M')
            party_end_str = party_end_dt.strftime('%H:%M')
            for line in rec.schedule_line_ids.filtered(lambda l: l.event in ['Party','Parti']):
                if rec.afterparty_ultra or rec.afterparty_service:
                    line.time = '22:30'
                else:
                    line.time = f'22:30 - {party_end_str}'

            for t in rec.transport_line_ids.filtered(lambda l: l.label in ['After Party Dönüş','After Parti Dönüş','After Parti Dönüşü','After Party Return']):
                if rec.afterparty_ultra or rec.afterparty_service:
                    t.time = end_str
                else:
                    t.time = ''

            for t in rec.transport_line_ids.filtered(lambda l: l.label in ['Çift Dönüş','Çift Dönüşü',"Couple's Return",'Guests Return']):
                if rec.afterparty_ultra or rec.afterparty_service:
                    later_dt = base_end_dt + timedelta(minutes=15)
                    t.time = later_dt.strftime('%H:%M')
                else:
                    t.time = '23:45'

    def _onchange_breakfast(self):
        for rec in self:
            if not rec.schedule_line_ids:
                continue

            old = bool(rec._origin.prehost_breakfast) if rec._origin else False
            new = bool(rec.prehost_breakfast)

            if old == new:
                continue
            first_transport = rec.transport_line_ids.sorted('sequence')[:1]
            if not first_transport:
                continue

            t = first_transport.time
            try:
                dt = datetime.strptime(t, '%H:%M')
            except (ValueError, TypeError):
                continue
            if (not old and new):
                dt_new = dt - timedelta(minutes=60)
            elif (old and not new):
                dt_new = dt + timedelta(minutes=60)
            else:
                continue

            first_transport.time = dt_new.strftime('%H:%M')



    @api.onchange('afterparty_ultra')
    def _onchange_afterparty_ultra(self):
        if self.afterparty_ultra and not self.afterparty_service:
            self.afterparty_ultra = False
            return {
                'warning': {
                    'title': _("Eksik Paket!"),
                    'message': _("Önce 'After Party' paketini seçmelisiniz."),
                }
            }

    @api.onchange('afterparty_street_food')
    def _onchange_street_food(self):
        if self.afterparty_street_food and not self.afterparty_service:
            self.afterparty_street_food = False
            return {
                'warning': {
                    'title': _("Eksik Paket!"),
                    'message': _("Sokak lezzetleri için önce 'After Party' paketi seçilmeli."),
                }
            }

    @api.onchange('afterparty_fog_laser')
    def _onchange_fog_laser(self):
        if self.afterparty_fog_laser and not self.afterparty_service:
            self.afterparty_fog_laser = False
            return {
                'warning': {
                    'title': _("Eksik Paket!"),
                    'message': _("Sis + Lazer gösterisi için önce 'After Party' paketi seçilmeli."),
                }
            }

    @api.onchange('afterparty_bbq_wraps')
    def _onchange_bbq_wraps(self):
        if self.afterparty_bbq_wraps and not (self.afterparty_service and self.afterparty_ultra):
            self.afterparty_bbq_wraps = False
            return {
                'warning': {
                    'title': _("Eksik Paket!"),
                    'message': _("Barbekü wraps için hem 'After Party' hem de 'Ultra' paketleri seçilmeli."),
                }
            }

    @api.constrains('afterparty_ultra', 'afterparty_street_food', 'afterparty_fog_laser', 'afterparty_bbq_wraps')
    def _check_afterparty_combinations(self):
        for rec in self:
            if rec.afterparty_ultra and not rec.afterparty_service:
                raise ValidationError(_("Ultra After Party, yalnızca After Party alındığında açılabilir."))
            if rec.afterparty_street_food and not rec.afterparty_service:
                raise ValidationError(_("Sokak lezzetleri için önce After Party seçilmelidir."))
            if rec.afterparty_fog_laser and not rec.afterparty_service:
                raise ValidationError(_("Sis + Lazer şovu için önce After Party seçilmelidir."))
            if rec.afterparty_bbq_wraps and not (rec.afterparty_service and rec.afterparty_ultra):
                raise ValidationError(
                    _("Barbekü wraps yalnızca After Party ve Ultra birlikte seçildiğinde aktif olabilir."))

    @api.onchange('dj_person')
    def _onchange_dj_person(self):
        for rec in self:
            if rec.project_id:
                rec.project_id.dj_person = rec.dj_person

    @api.depends('dj_person')
    def _sync_project(self):
        for rec in self:
            if rec.project_id and rec.project_id.dj_person != rec.dj_person:
                rec.project_id.dj_person = rec.dj_person

    def action_shift_plus(self):
        for rec in self:
            rec._shift_all_times(+rec.minutes)

    def action_shift_minus(self):
        for rec in self:
            rec._shift_all_times(-rec.minutes)

    # === Core ===
    def _shift_all_times(self, minutes_delta: int):
        """Kayıt içindeki tüm saat metinlerini dakika bazında kaydırır."""
        for rec in self:
            # start_end_time
            if isinstance(rec.start_end_time, str) and rec.start_end_time.strip():
                rec.start_end_time = self._shift_time_string(rec.start_end_time, minutes_delta)

            # schedule lines
            for line in rec.schedule_line_ids:
                if isinstance(line.time, str) and line.time.strip():
                    line.time = self._shift_time_string(line.time, minutes_delta)

            # transport lines
            for t in rec.transport_line_ids:
                if isinstance(t.time, str) and t.time.strip():
                    t.time = self._shift_time_string(t.time, minutes_delta)

    @staticmethod
    def _shift_time_string(text: str, minutes_delta: int) -> str:
        """
        Verilen metin içindeki TÜM HH:MM eşleşmelerini minutes_delta kadar kaydırır.
        '12:30 - 12:45' gibi aralıklarda iki ucu da kaydırır.
        """

        def _shift_match(m: re.Match) -> str:
            h = int(m.group(1))
            mnt = int(m.group(2))
            total = (h * 60 + mnt + minutes_delta) % (24 * 60)  # 24 saati sar
            nh, nm = divmod(total, 60)
            return f'{nh:02d}:{nm:02d}'

        return TIME_PATTERN.sub(_shift_match, text)


    @staticmethod
    def _format_date_tr(d):
        if not d:
            return ""
        if isinstance(d, str):
            try:
                d = fields.Date.from_string(d)
            except Exception:
                return d
        GUNLER = ['Pazartesi','Salı','Çarşamba','Perşembe','Cuma','Cumartesi','Pazar']
        AYLAR = ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']
        return f"{d.day} {AYLAR[d.month-1]} {GUNLER[d.weekday()]}"

    @staticmethod
    def _html_to_text(raw_html: str) -> str:
        """HTML -> düz metin (satır sonlarını koru)."""

        raw_html = raw_html or ''
        try:
            doc = lhtml.fromstring(raw_html or "<div/>")
            return (doc.text_content() or '').strip()
        except Exception:
            return re.sub(r'<[^>]+>', '', raw_html).strip()

    def _get_purchased_products_counter(self):
        """İlgili (sale/done) siparişlerdeki ürün adlarını ve toplam adetlerini döndürür."""
        counter = {}
        for so in self._get_related_confirmed_sale_orders():
            for line in so.sudo().order_line:
                name = (line.product_id.name or '').strip()
                if not name:
                    continue
                qty = int(line.product_uom_qty or 0)
                counter[name] = counter.get(name, 0) + qty
        return counter


    def _first_missing_for_changed_fields(self, vals: dict):
        """
        Bu write çağrısında değiştirilen TRACKED_FIELDS içinden,
        *yalnızca True yönüne geçenleri* kontrol eder.
        Şablonun dahil ettiği alanlar için kontrol yapılmaz.
        İlk eksik ürünü (field, label) döndürür; yoksa (None, None).
        """
        self.ensure_one()
        purchased = self._get_purchased_products_counter()
        included_fields = self._template_included_fields()

        for f in self.TRACKED_FIELDS:
            if f not in vals:
                continue
            if f in included_fields:
                continue

            new_val = vals[f]
            old_val = getattr(self, f)

            if not bool(new_val):
                continue
            if bool(old_val):
                continue

            labels = self._required_labels_for_field(f)
            for lbl in labels:
                if lbl not in purchased:
                    return f, lbl

        return None, None


    def _collect_coordinators(self):
        """Projeye bağlı ana siparişteki koordinatör isimlerini topla (varsa)."""
        self.ensure_one()
        order = self.project_id.sudo().reinvoiced_sale_order_id if self.project_id else False
        if not order:
            return ""
        names = []
        try:
            emps = order.coordinator_ids.mapped('employee_ids')
            if emps:
                names = [e.name for e in emps if e.name]
            if not names:
                names = [rec.name for rec in order.coordinator_ids if getattr(rec, 'name', False)]
        except Exception:
            pass
        return "-".join(dict.fromkeys(names))  # uniq + sırayı koru

    def _collect_demo_flag_packages(self):
        """
        Demo formundaki bayrak/seçimlerden paket etiketlerini üretir.
        Artık Barney, Fred, Saç&Makyaj, Konaklama, Dans Dersi, Müzik vb. hepsi dahil.
        """
        flag_labels = [
            # After Party ailesi
            ('afterparty_service', 'After Party'),
            ('afterparty_ultra', 'After Party Ultra'),
            ('afterparty_shot_service', 'Shot Servisi (After Party)'),
            ('afterparty_sushi', 'Sushi Bar'),
            ('afterparty_street_food', 'Street Food Atıştırmalık'),
            ('afterparty_fog_laser', 'Sis & Lazer'),
            ('afterparty_bbq_wraps', 'BBQ Dürümler'),

            # Foto/Video
            ('photo_video_plus', 'Photo & Video Plus'),
            ('photo_drone', 'Drone Kamera'),
            ('photo_yacht_shoot', 'Yacht Photo Shoot'),

            # Menü/Bar
            ('menu_hot_appetizer_ultra', 'Roket Karides'),
            ('bar_alcohol_service', 'Yabancı İçecek Servisi'),

            # Pre-hosting
            ('prehost_barney', 'Barney'),
            ('prehost_fred', 'Fred'),

            # Diğer hizmetler
            ('accommodation_service', 'Konaklama'),
            ('dance_lesson', 'Dans Dersi'),

            # Müzik (paketlerde de görmek istiyoruz)
            ('music_live', 'Canlı Müzik'),
            ('music_percussion', 'Perküsyon'),
            ('music_trio', 'TRIO'),

            # Demo içi “daha fazla içki” seçeneği
            ('afterparty_more_drinks', 'Daha Fazla Çeşit İçki (After party zamanı)'),
        ]

        out = []
        for f, label in flag_labels:
            if getattr(self, f):
                out.append(label)

        # Saç & Makyaj (hangi stüdyo olduğundan bağımsız)
        if getattr(self, 'hair_studio_3435', False) or getattr(self, 'hair_garage_caddebostan', False):
            out.append('Saç & Makyaj')

        # Kahvaltı (adetli olabilir)
        if getattr(self, 'prehost_breakfast', False):
            cnt = int(getattr(self, 'prehost_breakfast_count', 0) or 0)
            out.append("Kahvaltı" + (f" (x{cnt})" if cnt else ""))

        # Pasta opsiyonları (demodan da görünmesini istiyoruz)
        if getattr(self, 'cake_real', False):
            out.append("Pasta Show'da Gerçek Pasta")
        if getattr(self, 'cake_champagne_tower', False):
            out.append("Pasta Show'da Şampanya Kulesi")

        return list(dict.fromkeys(out))  # uniq + sırayı koru

    def _collect_packages(self):
        """
        Paketleri DEMO (öncelik) + SATIŞ (ekle) şeklinde birleştirir.
        Demo’da olanlar mutlaka görünür; satışta olup demoda olmayanlar sonradan eklenir.
        Kahvaltı satışta adetliyse (xN) ile yükseltilir.
        """
        demo_labels = list(dict.fromkeys(self._collect_demo_flag_packages()))

        purchased = self._get_purchased_products_counter()

        # Satış ürün adlarını etiketlere map’liyoruz
        MAPPING = [
            # After Party ailesi
            (['After Party Ultra'], 'After Party Ultra', False),
            (['After Party'], 'After Party', False),
            (['After Party Shot Servisi'], 'Shot Servisi (After Party)', False),
            (['Sushi Bar'], 'Sushi Bar', False),
            (['Fog + Laser Show'], 'Sis & Lazer', False),
            (['Street Food Atıştırmalık'], 'Street Food Atıştırmalık', False),
            (['BBQ Dürümler', 'BBQ Wraps'], 'BBQ Dürümler', False),
            (['Daha Fazla Çeşit İçki (After party zamanı)'], 'Daha Fazla Çeşit İçki (After party zamanı)', False),

            # Foto/Video
            (['Photo & Video Plus'], 'Photo & Video Plus', False),
            (['Drone Kamera'], 'Drone Kamera', False),
            (['Yacht Photo Shoot', 'Yat Çekimi', 'Yat Fotoğraf Çekimi'], 'Yacht Photo Shoot', False),

            # Menü/Bar
            (['Rocket Shrimp', 'Roket Karides'], 'Roket Karides', False),
            (['Yabancı İçecek Servisi', 'Yabancı İçki Servisi'], 'Yabancı İçecek Servisi', False),

            # Pre-hosting
            (['BARNEY', 'Barney'], 'Barney', False),
            (['FRED', 'Fred'], 'Fred', False),
            (['Breakfast Service', 'Kahvaltı'], 'Kahvaltı', True),  # adetli

            # Diğer hizmetler
            (['Konaklama'], 'Konaklama', False),
            (['Dans Dersi'], 'Dans Dersi', False),

            # Müzik
            (['Canlı Müzik'], 'Canlı Müzik', False),
            (['Perküsyon'], 'Perküsyon', False),
            (['TRIO', 'Trio'], 'TRIO', False),

            # Pasta opsiyonları
            (["Pasta Show'da Gerçek Pasta"], "Pasta Show'da Gerçek Pasta", False),
            (["Pasta Show'da Şampanya Kulesi"], "Pasta Show'da Şampanya Kulesi", False),

            # Ek örnekler (satışta kullanıyorsan)
            (['Eğlence Uzatma(1 Saat)'], 'Eğlence Uzatma(1 Saat)', False),
            (['Canlı Müzik + Perküsyon'], 'Canlı Müzik + Perküsyon', False),
            (['Canlı Müzik Özel'], 'Canlı Müzik Özel', False),
            (['Canlı Müzik + Perküsyon + TRIO'], 'Canlı Müzik + Perküsyon + TRIO', False),
        ]

        merged, seen = list(demo_labels), set(demo_labels)

        for names, label, show_qty in MAPPING:
            total = sum(purchased.get(n, 0) for n in names)
            if not total:
                continue

            # Demo’da zaten varsa ve adet gerekmiyorsa tekrar eklemeyelim
            if label in seen and not show_qty:
                continue

            text = f"{label} (x{int(total)})" if show_qty else label

            # Kahvaltı gibi adetli etikette demoda adetsiz varsa → yükselt
            if show_qty and label in seen:
                try:
                    idx = merged.index(label)  # demoda "Kahvaltı" var (adetsiz)
                    merged[idx] = text  # satış adediyle güncelle
                except ValueError:
                    if text not in seen:
                        merged.append(text)
                        seen.add(text)
                continue

            if text not in seen:
                merged.append(text)
                seen.add(text)

        return merged

    def _collect_program(self):
        """Program akışı başlığı ve satırları (schedule_line_ids) + satır notları (HAM HTML)."""
        EVENT_TR = {
            'Cocktail': 'Kokteyl', 'Kokteyl': 'Kokteyl',
            'Ceremony': 'Seremoni', 'Seremoni': 'Seremoni',
            'Dinner': 'Yemek', 'Yemek': 'Yemek',
            'Party': 'Eğlence', 'Parti': 'Eğlence',
            'After Party': 'After Party', 'After Parti': 'After Party',
        }
        lines = []
        for ln in self.schedule_line_ids.sorted('sequence')[1:]:
            ev = (ln.event or '').strip()
            ev_tr = EVENT_TR.get(ev, ev or '-')
            tm = (ln.time or '').strip()
            base = f"➖{ev_tr}:  {tm}" if tm else f"➖{ev_tr}"
            lines.append(base)

        header = (self.start_end_time or '').replace(' ', '')
        return header, lines

    def _collect_transports(self):
        """Tekne/ulaşım satırları (transport_line_ids).
        - 'dönüş' içeren etiketlerde birden fazla liman varsa ayrı satırlar üretir.
        - Satır notlarını HAM HTML ekler.
        - Listenin en altına 'Ertesi gün çift dönüşü:' maddesini ekler (listede yoksa).
        """
        import re
        out = []
        i = 1

        for t in self.transport_line_ids.sorted('sequence'):
            label = (t.label or '').strip()
            tm = (t.time or '').strip()

            ports = [p.name.strip() for p in t.port_ids] if t.port_ids else []
            # other_port = (t.other_port or '').strip()
            # if other_port:
            #     extra = [p.strip() for p in re.split(r'[,\-/;–—·•]+', other_port) if p.strip()]
            #     for p in extra:
            #         if p not in ports:
            #             ports.append(p)

            # HAM HTML not
            is_return = 'dönüş' in label.lower() or 'dönüşü' in label.lower()

            if is_return and len(ports) > 1:
                for p in ports:
                    line = f"{i}/ {label}: {tm} {p}".rstrip()
                    out.append(line)
                    i += 1
            else:
                suffix = f" {', '.join(ports)}" if ports else ""
                line = f"{i}/ {label}: {tm}{suffix}".rstrip()
                out.append(line)
                i += 1


        out.append(f"{i}/ Ertesi gün çift dönüşü: haber vereceğim.")

        return out

    def _collect_decor_notes(self):
        """Dekor başlıkları & seçilenler."""
        # isimleri topla
        def names(m2m):
            return ', '.join(rec.name for rec in m2m) if m2m else ''
        theme = names(self.table_theme_ids)
        runner = names(self.table_runner_design_ids)
        colors = names(self.table_color_ids)
        charger = names(self.table_charger_ids)
        tag = getattr(self.table_tag_ids, 'name', '') or ''

        cake = names(self.cake_choice_ids)
        cake_bits = []
        if self.cake_real:
            cake_bits.append("Gerçek Pasta")
        if self.cake_champagne_tower:
            cake_bits.append("Şampanya Kulesi")
        if cake:
            cake_bits.insert(0, cake)
        cake_txt = ', '.join(cake_bits)

        flower = ("Canlı" if self.table_fresh_flowers else "") or ("Kuru" if self.table_dried_flowers else "")
        notes = self._html_to_text(self.table_description)

        lines = []
        if cake_txt: lines.append(f"➖Pasta : {cake_txt}")
        if theme:    lines.append(f"➖Süsleme : {theme}")
        if runner:   lines.append(f"➖Kumaş : {runner}")
        if colors:   lines.append(f"➖Renk : {colors}")
        if flower:   lines.append(f"➖Çiçek : {flower}")
        if charger:  lines.append(f"➖Supla : {charger}")
        if tag:      lines.append(f"➖Tag : {tag}")
        if notes:    lines.append(f"➖Dekor notu :\n{notes}")
        return lines

    def _collect_music_notes(self):
        """Eğlence başlıkları."""
        bits = []
        if self.music_live:        bits.append("Canlı müzik Var")
        else:        bits.append("Canlı müzik Yok")
        if self.music_percussion:  bits.append("Perküsyon Var")
        else:  bits.append("Perküsyon Yok")
        if self.music_trio:        bits.append("Trio Var")
        else: bits.append("Trio Yok")
        if self.afterparty_service and self.afterparty_ultra:
            bits.append("After Party Ultra var")
        elif self.afterparty_service:
            bits.append("After Party var")
        if self.afterparty_bbq_wraps: bits.append("BBQ Dürümleri")
        if self.afterparty_shot_service: bits.append("Shot Servisi")
        if self.afterparty_fog_laser: bits.append("Sis & Laser")
        if self.afterparty_sushi:     bits.append("Sushi")
        if self.afterparty_street_food:     bits.append("Street Food Atıştırmalık")
        #if self.music_other and self.music_other_details:
        #     bits.append(f"Özel: {self.music_other_details}")
        # if self.cocktail_request:
        #     bits.append("Kokteyl istek listesi mevcut")
        # if self.dinner_request:
        #     bits.append("Yemek istek listesi mevcut")
        # if self.party_request:
        #     bits.append("Parti istek listesi mevcut")
        # if self.afterparty_request:
        #     bits.append("After Party istek listesi mevcut")
        # if self.ban_songs:
        #     bits.append("Yasaklı şarkı listesi mevcut")

        out = []
        if bits:
            out.append("▶️ " + ", ".join(bits) + ".")
        return out

    def _collect_general_notes(self):
        self.ensure_one()
        CEREMONY_MAP = {'actual': 'Gerçek', 'staged': 'Mizansen', 'def': 'Seçili değil'}
        lines = []

        if self.ceremony:
            lines.append(f"➖Nikah : {CEREMONY_MAP.get(self.ceremony, self.ceremony)}")

        if self.accommodation_service:
            acc = self.accommodation_hotel or "Var"
            lines.append(f"➖Konaklama : {acc}")

        if getattr(self, 'merasim', False):
            sel = self.with_context(lang=self.env.user.lang).fields_get(['merasim'])['merasim']['selection']
            merasim_label = dict(sel).get(self.merasim, self.merasim)
            lines.append(f"➖Merasim : {merasim_label}")
        ceremony_call='➖Takı Anonsu: VAR' if self.ceremony_call else '➖Takı Anonsu: YOK'
        lines.append(ceremony_call)
        ceremony = 'VAR' if getattr(self, 'is_ceremony', False) else 'YOK'
        lines.append(f'➖Seremoni Düzeni : {ceremony}')


        pre = []
        if getattr(self, 'prehost_barney', False): pre.append('Barney')
        if getattr(self, 'prehost_fred', False):   pre.append('Fred')
        if pre:
            lines.append("➖Pre-hosting : " + ", ".join(pre))

        # Sosyal medya tag
        if getattr(self, 'other_social_media_tag', False):
            sm = "Var"
            if getattr(self, 'other_social_media_details', False):
                sm += f" – {self.other_social_media_details}"
        else:
            sm = "Yok"
        lines.append(f"➖Sosyal Medya Tag : {sm}")
        lines.append(", ".join([
            f"➖Canlı Müzik: {'VAR' if self.music_live else 'YOK'}",
            f"Trio: {'VAR' if self.music_trio else 'YOK'}",
            f"Perküsyon: {'VAR' if self.music_percussion else 'YOK'}",
        ]))

        for html in [getattr(self, 'other_description', '') or '',
                     getattr(self, 'additional_services_description', '') or '']:
            if html and str(html).strip():
                lines.append(html)  # HAM HTML
                lines.append("&nbsp;")  # boşluk

        return lines

    def _collect_treats(self):
        """İkramlar / menü özetleri."""
        # selection etiketleri
        HOT_APP_MAP = dict(self._fields['menu_hot_appetizer']._description_selection(self.env))
        hot_app = HOT_APP_MAP.get(self.menu_hot_appetizer) if self.menu_hot_appetizer else ""
        # m2m isimleri
        def names(m2m):
            return ', '.join(rec.name for rec in m2m) if m2m else ''
        meze = names(self.menu_meze_ids)
        dessert = names(self.menu_dessert_ids)
        dessert_ultra = names(self.menu_dessert_ultra_ids)

        lines = []
        if hot_app:           lines.append(f"➖Sıcak Başlangıç : {hot_app}")
        if self.menu_hot_appetizer_ultra: lines.append("➖Sıcak Ekstra : Rocket Shrimp")
        if meze:              lines.append(f"➖Mezeler : {meze}")
        if dessert:           lines.append(f"➖Tatlı : {dessert}")
        if dessert_ultra:     lines.append(f"➖Ultra Tatlı : {dessert_ultra}")
        if self.afterparty_street_food: lines.append("➖Sokak Lezzetleri")
        if self.bar_alcohol_service:
            # Raki markası (seçiliyse)
            RAKI = dict(self._fields['bar_raki_brand']._description_selection(self.env))
            raki = RAKI.get(self.bar_raki_brand) if self.bar_raki_brand else ""
            lines.append("➖Alkol servisi" + (f" – {raki}" if raki else ""))
        return lines

    def _display_wedding_type(self):
        # Öncelik: satış şablonunun adı
        if self.sudo().sale_template_id and self.sudo().sale_template_id.name:
            return self.sudo().sale_template_id.name
        # Aksi halde selection label
        try:
            MP = dict(self._fields['wedding_type']._description_selection(self.env))
            return MP.get(self.wedding_type) or ""
        except Exception:
            return self.wedding_type or ""

    def _display_dj(self):
        DJ_MAP = {'engin': 'Engin', 'fatih': 'Fatih', 'other': 'Diğer'}
        return DJ_MAP.get(self.dj_person) or ("Diğer" if self.music_other else "")

    def _collect_menu_bar_notes(self):
        """Menü ve Bar notları (ham HTML notlar en altta)."""
        self.ensure_one()
        lines, notes = [], []

        # Menü seçimi/özetleri
        hot_map = dict(
            self.with_context(lang=self.env.user.lang).fields_get(['menu_hot_appetizer'])['menu_hot_appetizer'][
                'selection'])
        if self.menu_hot_appetizer:
            lines.append(f"➖Sıcak Başlangıç : {hot_map.get(self.menu_hot_appetizer, self.menu_hot_appetizer)}")
        if self.menu_hot_appetizer_ultra:
            lines.append("➖Sıcak Ekstra : Rocket Shrimp")

        def names(m2m):
            return ", ".join(m2m.mapped('name')) if m2m else ""

        if self.menu_meze_ids:
            lines.append(f"➖Mezeler : {names(self.menu_meze_ids)}")
        if self.menu_dessert_ids:
            lines.append(f"➖Tatlı : {names(self.menu_dessert_ids)}")
        if self.menu_dessert_ultra_ids:
            lines.append(f"➖Ultra Tatlı : {names(self.menu_dessert_ultra_ids)}")

        # Bar
        raki_map = dict(
            self.with_context(lang=self.env.user.lang).fields_get(['bar_raki_brand'])['bar_raki_brand']['selection'])
        if self.bar_alcohol_service:
            lines.append("➖Yabancı İçecek Servisi : Var")
        else:
            lines.append("➖Yabancı İçecek Servisi : Yok")
            if self.bar_purchase_advice:
                notes.append(f"{self.bar_purchase_advice}")  # ham HTML olabilir
        if self.alcohol_service:
            lines.append("➖Alkol Servisi : Var")
        else:
            lines.append("➖Alkol Servisi : Yok")

        if self.bar_raki_brand:
            lines.append(f"➖Rakı Markası : {raki_map.get(self.bar_raki_brand, self.bar_raki_brand)}")

        # HTML notlar ham olarak
        if self.menu_meze_notes and str(self.menu_meze_notes).strip():
            notes.append(self.menu_meze_notes)
        if self.menu_description and str(self.menu_description).strip():
            notes.append(self.menu_description)
        if self.bar_description and str(self.bar_description).strip():
            notes.append(self.bar_description)

        if getattr(self, "prehost_breakfast", False):
            cnt = f" ({int(self.prehost_breakfast_count)}px)" if self.prehost_breakfast_count else ""
            lines.append(f"➖Kahvaltı Servisi {cnt}")

        # After Party F&B
        af_items = []
        if getattr(self, "afterparty_shot_service", False): af_items.append("Shot Servisi")
        if getattr(self, "afterparty_bbq_wraps", False):    af_items.append("BBQ Dürümleri")
        if getattr(self, "afterparty_sushi", False) or getattr(self, "afterparty_street_food", False):
            af_items.append("Street Food Atıştırmalık")
        if af_items:
            lines.append("➖After Party : " + ", ".join(af_items))
        if getattr(self, "afterparty_more_drinks", False):
            lines.append("➖After Party İçecekleri : Daha fazla çeşit içki")

        if notes:
            lines.extend(notes)

        return lines

    def _build_whatsapp_message(self):
        from markupsafe import escape as E  # yoksa: E = html_escape
        self.ensure_one()

        tarih = self._format_date_tr(self.invitation_date or self.demo_date)
        tip = self._display_wedding_type() or "-"
        guest = f"{int(self.guest_count)} misafir" if self.guest_count else "-"
        expected = "-"  # Ayrı alan varsa bağlayın
        koordinatör = self._collect_coordinators() or "-"
        dj = self._display_dj() or "-"

        packages = self._collect_packages()
        program_header, program_lines = self._collect_program()  # program_lines: HTML içerebilir
        transport_lines = self._collect_transports()  # HTML içerebilir
        genel = self._collect_general_notes()  # HTML içerebilir
        dekor = self._collect_decor_notes()  # metin
        muzik = self._collect_music_notes()  # metin
        mb_lines = self._collect_menu_bar_notes()  # HTML içerebilir
        program_notes=self.schedule_description or ''
        transport_notes=self.transportation_description or ''

        def ul(items, escape_html=True):
            ul_style = "list-style:none; margin:0; padding-left:0;"
            li_style = "list-style:none; margin:0; padding:0;"
            items = [i for i in (items or []) if (i or "").strip() != ""]
            if not items:
                return f"<ul style='{ul_style}'><li style='{li_style}'>-</li></ul>"
            buff = [f"<ul style='{ul_style}'>"]
            for it in items:
                if escape_html:
                    buff.append(f"<li style='{li_style}'>{E(str(it))}</li>")
                else:
                    buff.append(f"<li style='{li_style}'>{it}</li>")  # ham HTML
            buff.append("</ul>")
            return "".join(buff)

        important_html = (self.special_notes or "").strip()

        html = f"""
        <div>
          <p>🏁 <b>Tarih:</b> {E(tarih)}</p>
          <p>👩‍❤️‍👨 <b>Çiftimiz:</b> {E(self.project_id.sudo().reinvoiced_sale_order_id.opportunity_id.name or '')}</p>
          <p>🔳 <b>Düğün Tipi:</b> {E(tip)}</p>
          <p>🟡 <b>Kişi sayısı:</b> {E(guest)}</p>
          <p>🟢 <b>Beklenen:</b> {E(expected)}</p>
          <p>👧 <b>Koordinatör:</b> {E(koordinatör)}</p>
          <p>🎧 <b>DJ:</b> {E(dj)}</p><br/>

          <h4>➕ Ek Paketler:</h4>
          {ul(packages)}  <!-- metin; escape ON -->

          <h4>🕖 Program Akışı{f": {E(program_header)}" if program_header else ""}</h4>
          {ul(program_lines, escape_html=False)}  <!-- satır notları HAM HTML -->
          {Markup(program_notes)}

          <h4>⚓️ Tekne Saatleri:</h4>
          {ul(transport_lines, escape_html=False)}  <!-- satır notları HAM HTML -->
            {Markup(transport_notes)}
          <h4>🔴 Genel Notlar:</h4>
          {ul(genel, escape_html=False)}  <!-- HTML notlar & sosyal medya -->

          <h4>⚜️ Dekor Notları:</h4>
          {ul(dekor)}  <!-- metin -->

          <h4>🍽️ Menü & 🍸 Bar Notları:</h4>
          {ul(mb_lines, escape_html=False)}  <!-- HTML notlar mümkün -->

          <h4>🎶 Eğlence Notları:</h4>
          {ul(muzik)}  <!-- metin -->

          <h4>‼️Önemli Notlar:</h4>
          {important_html if important_html else "-"}
        </div>
        """.strip()
        return html
    # === Buton aksiyonu ===
    def action_generate_whatsapp_message(self):
        self.ensure_one()
        for rec in self:
            html_body = rec._build_whatsapp_message()
            ctx = {
                'default_model': self._name,
                'default_res_ids': [self.id],
                'default_composition_mode': 'comment',  # e-posta değil, chatter yorumu
                'default_is_log': True,  # İç Not (log) olarak işaretle
                'default_subtype_id': self.env.ref('mail.mt_note').id,  # Not alt tipi
                'default_subject': 'WhatsApp Mesajı',
                'default_body': html_body,  # HTML gövde (escape edilmemiş)
            }

            view = self.env.ref('mail.email_compose_message_wizard_form')
            return {
                'type': 'ir.actions.act_window',
                'name': 'Log Ekle (WhatsApp)',
                'res_model': 'mail.compose.message',
                'view_mode': 'form',
                'view_id': view.id,
                'target': 'new',
                'context': ctx,
            }
        return True

    @api.model
    def create(self, vals):
        if 'name' in vals and vals.get('name') == _('New Demo Form'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'project.demo.form') or vals['name']

        rec = super(ProjectDemoForm, self).create(vals)

        rec._onchange_start_end_time()
        rec._onchange_breakfast()

        return rec

    def write(self, vals):
        if any(rec.confirmed_demo_form_plan for rec in self) and not self.env.user.has_group('base.group_system'):
            raise UserError("Onaylanmış kayıtta değişiklik yapılamaz.")

        if not (self.env.context.get('extra_protocol_confirmed') or
                self.env.context.get('skip_extra_protocol_check')):
            changed_tracked = set(vals) & set(self.TRACKED_FIELDS)
            if changed_tracked:
                for rec in self:
                    field_name, missing_label = rec._first_missing_for_changed_fields(vals or {})
                    if missing_label:
                        action_id = self.env.ref('demo_form.action_project_demo_extra_protocol_wizard').id
                        msg = _(
                            "%s ürünü onaylı tekliflerde bulunamadı.\n\nEk Protokol görevi açılsın mı? \n\n“Görevi açmadan devam etmek isterseniz bu uyarıyı kapattıktan sonra sol üstten çarpıya (Discard) basın.") % missing_label
                        raise RedirectWarning(
                            msg,
                            action_id,
                            _("Görevi Aç"),
                            additional_context={
                                'default_demo_id': rec.id,
                                'default_product_label': missing_label,
                                'default_pending_vals_json': json.dumps(vals, ensure_ascii=False),
                            }
                        )
        res = super().write(vals)

        for rec in self:
            if any(f in vals for f in ('afterparty_service', 'afterparty_ultra', 'afterparty_dance_show')):
                rec._onchange_afterparty_ultra_open()
                rec._onchange_afterparty_service_open()
                rec._onchange_start_end_time()
            if 'prehost_breakfast' in vals:
                rec._onchange_breakfast()
            if 'afterparty_ultra' in vals:
                rec._onchange_afterparty_ultra()
            if 'afterparty_street_food' in vals:
                rec._onchange_street_food()
            if 'afterparty_fog_laser' in vals:
                rec._onchange_fog_laser()
            if 'afterparty_bbq_wraps' in vals:
                rec._onchange_bbq_wraps()

        return res