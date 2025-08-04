from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError
from lxml import html as lhtml
from markupsafe import escape as html_escape
import re


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
    invitation_owner = fields.Char(string="Invitation Owner")
    invitation_date = fields.Date(string="Invitation Date")
    duration_days = fields.Char(string="Day", compute='_compute_day')
    demo_date = fields.Date(string="Demo Date")
    special_notes = fields.Html(string="Special Notes")

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
    start_end_time = fields.Char(string="Start-End Time")

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
        string="Accommodation Provided",
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
    photo_homesession = fields.Boolean(string="Home Session")
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
    music_dj_fatih = fields.Boolean(string="DJ: Fatih Aşçı")
    music_dj_engin = fields.Boolean(string="DJ: Engin Sadiki")
    music_other = fields.Boolean(string="Other")
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

    @api.depends('special_notes')
    def _compute_split_notes(self):
        limit = 150
        for rec in self:
            raw_html = rec.special_notes or ''
            # HTML içinden düz metin çıkar
            try:
                doc = lhtml.fromstring(raw_html or "<div/>")
                notes = doc.text_content().strip()
            except Exception:
                # fallback: basit regex ile tag kaldır
                notes = re.sub(r'<[^>]+>', '', raw_html).strip()

            if len(notes) <= limit:
                preview = notes
                remaining = ''
            else:
                preview_candidate = notes[:limit]
                last_space = preview_candidate.rfind(' ')
                if last_space > 0:
                    preview = preview_candidate[:last_space]
                    remaining = notes[last_space + 1:].lstrip()
                else:
                    preview = preview_candidate
                    remaining = notes[limit:].lstrip()

            # HTML alanlara güvenli şekilde ver; satır sonlarını koru
            preview_html = f"<div>{html_escape(preview).replace(chr(10), '<br/>')}</div>"
            remaining_html = f"<div>{html_escape(remaining).replace(chr(10), '<br/>')}</div>" if remaining else ''

            rec.special_notes_preview = preview_html
            rec.special_notes_remaining = remaining_html

    @api.model
    def create(self, vals):
        if 'name' in vals and vals.get('name') == _('New Demo Form'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'project.demo.form') or vals['name']
        return super().create(vals)

    @api.depends('invitation_date')
    def _compute_day(self):
        turkish_days = [
            'Pazartesi', 'Salı', 'Çarşamba',
            'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'
        ]
        for rec in self:
            if rec.invitation_date:
                dt = fields.Date.from_string(rec.invitation_date)
                rec.duration_days = turkish_days[dt.weekday()]
            else:
                rec.duration_days = False

    def _onchange_start_end_time(self):
        for rec in self:
            # remove existing related lines
            to_remove = rec.schedule_line_ids.filtered(
                lambda l: l.event in ('After Party Ultra', 'After Party', 'Dance Show')
            )
            to_remove_transport = rec.transport_line_ids.filtered(
                lambda l: l.label in ('After Party Ultra', 'After Party', 'Dance Show')
            )

            if to_remove:
                rec.schedule_line_ids = [(3, l.id) for l in to_remove]
            if to_remove_transport:
                rec.transport_line_ids = [(3, l.id) for l in to_remove_transport]

            # compute start / end
            start = '19:30'
            if rec.afterparty_ultra:
                base_end = '02:00'
            elif rec.afterparty_service:
                base_end = '01:30'
            else:
                base_end = '23:30'

            if rec.afterparty_dance_show:
                try:
                    dt = datetime.strptime(base_end, '%H:%M') + timedelta(minutes=15)
                    end = dt.strftime('%H:%M')
                except ValueError:
                    end = base_end
            else:
                end = base_end

            rec.start_end_time = f"{start} - {end}"

            choice = False
            if rec.afterparty_ultra:
                choice = 'After Party Ultra'
            elif rec.afterparty_service:
                choice = 'After Party'
            elif rec.afterparty_dance_show:
                choice = 'Dance Show'

            try:
                after_end_dt = datetime.strptime(end, '%H:%M')
            except ValueError:
                after_end_dt = None

            if choice:
                schedule_cmds = []
                existing_s = rec.schedule_line_ids.sorted('sequence')
                if existing_s:
                    last_s = existing_s[-1]
                    old_seq = last_s.sequence
                    if after_end_dt:
                        new_last_time = (after_end_dt + timedelta(minutes=15)).strftime('%H:%M')
                    else:
                        new_last_time = last_s.time
                    schedule_cmds.append((1, last_s.id, {'sequence': old_seq + 1, 'time': new_last_time}))
                    schedule_cmds.append((0, 0, {
                        'sequence': old_seq,
                        'event': choice,
                        'time': f'23:30 - {end}',
                    }))
                else:
                    schedule_cmds.append((0, 0, {
                        'sequence': 1,
                        'event': choice,
                        'time': f'23:30 - {end}',
                    }))
                    if after_end_dt:
                        later_time = (after_end_dt + timedelta(minutes=15)).strftime('%H:%M')
                    else:
                        later_time = end
                    schedule_cmds.append((0, 0, {
                        'sequence': 2,
                        'event': f"{choice} Follow-up",
                        'time': f'23:30 - {later_time}',
                    }))
                rec.schedule_line_ids = schedule_cmds

                existing_t = rec.transport_line_ids.sorted('sequence')
                if existing_t:
                    last_t = existing_t[-1]
                    rec.transport_line_ids = [(1, last_t.id, {'time': end})]

    def _onchange_breakfast(self):
        for rec in self:
            # get the first schedule line
            lines = rec.schedule_line_ids.sorted('sequence')
            transport_lines=rec.transport_line_ids
            if not lines:
                continue
            first = lines[0]
            first_transport=transport_lines[0]
            try:
                dt = datetime.strptime(first.time, '%H:%M')
                dt_transport=datetime.strptime(first_transport.time,'%H:%M')
            except (ValueError, TypeError):
                continue
            # subtract or add 30 minutes
            if rec.prehost_breakfast:
                dt_new = dt - timedelta(minutes=30)
                dt_new_transport=dt_transport-timedelta(minutes=30)
            else:
                dt_new = dt + timedelta(minutes=30)
                dt_new_transport = dt_transport + timedelta(minutes=30)
            first.time = dt_new.strftime('%H:%M')
            first_transport.time = dt_new_transport.strftime('%H:%M')

    def write(self, vals):
        res = super().write(vals)

        for rec in self:
            if any(f in vals for f in ('afterparty_service', 'afterparty_ultra', 'afterparty_dance_show')):
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
