from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError
from lxml import html as lhtml
from markupsafe import escape as html_escape
import re
import json
from html import escape as E

TIME_PATTERN = re.compile(r'(\d{1,2}):([0-5]\d)')


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
    dj_person = fields.Selection([('engin', 'DJ: Engin Sadiki'), ('fatih', 'DJ: Fatih Aşçı'), ('other', 'Diğer')],
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

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )
    minutes = fields.Integer(string='Adjust Time')

    missing_products_json = fields.Text(
        string="Eksik Opsiyonlar (JSON)",
        copy=False, tracking=True,
        help="Demo Form'da aktif olup satışlarda karşılığı olmayan ürünlerin JSON listesi."
    )

    PRODUCT_REQUIREMENTS = {
        'photo_video_plus': ['Photo & Video Plus'],
        'photo_drone': ['Drone Kamera'],
        'photo_harddisk_delivered': {
            'delivered': ['Hard Disk 1TB Delivered'],
            'later': ['Will Deliver Later'],
        },
        'afterparty_service': ['After Party'],
        'afterparty_ultra': ['After Party Ultra'],
        'afterparty_shot_service': ['After Party Shot Servisi'],
        'afterparty_sushi': ['Sushi Bar'],
        'afterparty_dance_show': ['Dans Show'],
        'afterparty_fog_laser': ['Fog + Laser Show'],
        'bar_alcohol_service': ['Yabancı İçki Servisi'],
        'hair_studio_3435': ['Saç & Makyaj'],
        'hair_garage_caddebostan': ['Saç & Makyaj'],
        'cake_real': ["Pasta Show'da Gerçek Pasta"],
        'cake_champagne_tower': ["Pasta Show'da Şampanya Kulesi"],
        'prehost_barney': ['BARNEY'],
        'prehost_fred': ['FRED'],
        'prehost_breakfast': ['Breakfast Service'],
    }
    TRACKED_FIELDS = list(PRODUCT_REQUIREMENTS.keys())

    # ---- Yardımcılar ----
    def _get_missing_list(self):
        try:
            return json.loads(self.missing_products_json or '[]')
        except Exception:
            return []

    def _set_missing_list(self, arr):
        self.missing_products_json = json.dumps(sorted(set(arr)), ensure_ascii=False)

    def _get_related_confirmed_sale_orders(self):
        """Bu projenin bağlı olduğu CRM fırsatındaki onaylı (sale/done) tüm siparişler."""
        self.ensure_one()
        base_order = self.project_id and self.project_id.reinvoiced_sale_order_id
        opp = base_order.opportunity_id if base_order else False
        if not opp:
            return self.env['sale.order']
        return self.env['sale.order'].sudo().search([
            ('opportunity_id', '=', opp.id),
            ('state', 'in', ('sale', 'done')),
        ])

    def _get_purchased_product_names(self):
        """İlgili sipariş satırlarından ürün adlarını topla."""
        names = set()
        for so in self._get_related_confirmed_sale_orders():
            for l in so.order_line:
                n = (l.product_id.name or '').strip()
                if n:
                    names.add(n)
        return names

    def _collect_required_products_from_demo(self):
        """Demo Form'da aktif seçilmiş opsiyonlardan beklenen ürünleri üretir."""
        req = set()
        for field, mapping in self.PRODUCT_REQUIREMENTS.items():
            val = getattr(self, field)
            if not val:
                continue
            if field == 'photo_harddisk_delivered':
                prods = mapping.get(val) or []
            else:
                prods = mapping
            req.update(prods)
        return req

    def _compute_missing_products(self):
        """Aktif opsiyonlar – satın alınmış ürünler = eksikler."""
        required = self._collect_required_products_from_demo()
        purchased = self._get_purchased_product_names()
        missing = sorted(p for p in required if p not in purchased)
        return missing

    def _sync_missing_activity_and_chatter(self, prev_missing, new_missing):
        """Eksik listesi değişiminde chatter ve aktiviteyi yönetir."""
        if set(prev_missing) == set(new_missing):
            return

        # Mesaj gövdesi
        parts = []
        added = sorted(set(new_missing) - set(prev_missing))
        removed = sorted(set(prev_missing) - set(new_missing))
        if added:
            parts.append(_("<b>Eksik</b> (satın alınmamış) opsiyonlar eklendi: %s") % ", ".join(added))
        if removed:
            parts.append(_("Aşağıdaki opsiyonlar artık satışlarda mevcut: %s") % ", ".join(removed))
        if not parts:
            parts.append(_("Liste güncellendi."))

        if new_missing:
            parts.append(_("<b>Öneri:</b> Bu opsiyonlar için <i>Ek Protokol</i> teklifi açılmalı."))

        self.message_post(
            body="<br/>".join(parts),
            subtype_xmlid='mail.mt_note'
        )

        Activity = self.env['mail.activity'].sudo()
        todo_type = self.env.ref('mail.mail_activity_data_todo')

        # Mevcut açık ToDo'yu bul
        act = Activity.search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id),
            ('activity_type_id', '=', todo_type.id),
            ('state', '=', 'planned'),
            ('summary', '=', 'Eksik satın alınan opsiyonlar'),
        ], limit=1)

        if new_missing:
            note = _(
                "Aşağıdaki opsiyonlar Demo Form’da aktif, ancak ilgili satışlarda ürün bulunmuyor:\n- %s\n\nLütfen Ek Protokol teklifi oluşturun.") % (
                       "\n- ".join(new_missing)
                   )
            vals = {
                'res_model_id': self.env['ir.model']._get_id(self._name),
                'res_model': self._name,
                'res_id': self.id,
                'activity_type_id': todo_type.id,
                'summary': 'Eksik satın alınan opsiyonlar',
                'note': note,
                'user_id': self.project_id.user_id.id or self.env.user.id,
                'date_deadline': fields.Date.today(),
            }
            if act:
                act.write({'note': note})
            else:
                Activity.create(vals)
        else:
            if act:
                act.action_feedback(feedback=_("Tüm opsiyonlar satışlarda mevcut; aktivite tamamlandı."))
            if prev_missing:
                self.message_post(
                    body=_("Eksik opsiyon listesi boşaldı; aktivite tamamlandı."),
                    subtype_xmlid='mail.mt_note'
                )

    def action_refresh_missing_requirements(self):
        for rec in self:
            prev = rec._get_missing_list()
            new = rec._compute_missing_products()
            rec._set_missing_list(new)
            rec._sync_missing_activity_and_chatter(prev, new)

    @api.depends('special_notes')
    def _compute_split_notes(self):
        limit = 300
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

    def action_refresh_missing_requirements(self):
        for rec in self:
            prev = rec._get_missing_list()
            new = rec._compute_missing_products()
            rec._set_missing_list(new)
            rec._sync_missing_activity_and_chatter(prev, new)

    @api.model
    def create(self, vals):
        if 'name' in vals and vals.get('name') == _('New Demo Form'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'project.demo.form') or vals['name']

        rec = super(ProjectDemoForm, self).create(vals)

        rec._onchange_start_end_time()
        rec._onchange_breakfast()
        prev = rec._get_missing_list()
        new = rec._compute_missing_products()
        rec._set_missing_list(new)
        rec._sync_missing_activity_and_chatter(prev, new)

        return rec

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
            # 1) Orijinal base end time
            if rec.afterparty_ultra:
                base_end_dt = datetime.strptime('02:00', '%H:%M')
            elif rec.afterparty_service:
                base_end_dt = datetime.strptime('01:30', '%H:%M')
            else:
                base_end_dt = datetime.strptime('23:30', '%H:%M')

            end_dt = base_end_dt + (timedelta(minutes=15) if rec.afterparty_dance_show else timedelta())
            end_str = end_dt.strftime('%H:%M')

            rec.start_end_time = f'19:30-{end_str}'

            for line in rec.schedule_line_ids.filtered(lambda l: l.event in ['After Party','After Parti']):
                if rec.afterparty_ultra or rec.afterparty_service:
                    line.time = f'23:30 - {end_str}'
                else:
                    line.time = ''


            party_end_dt = datetime.strptime('23:30', '%H:%M') + (
                timedelta(minutes=15) if rec.afterparty_dance_show else timedelta())
            party_end_str = party_end_dt.strftime('%H:%M')
            for line in rec.schedule_line_ids.filtered(lambda l: l.event in ['Party','Parti']):
                if rec.afterparty_ultra or rec.afterparty_service:
                    line.time = '22:30'
                else:
                    line.time = f'22:30 - {party_end_str}'

            for t in rec.transport_line_ids.filtered(lambda l: l.label in ['After Party Dönüş','After Parti Dönüş']):
                if rec.afterparty_ultra or rec.afterparty_service:
                    t.time = end_str
                else:
                    t.time = ''

            for t in rec.transport_line_ids.filtered(lambda l: l.label == 'Çift Dönüş'):
                if rec.afterparty_ultra or rec.afterparty_service:
                    later_dt = base_end_dt + timedelta(minutes=15)
                    if rec.afterparty_dance_show:
                        later_dt += timedelta(minutes=15)
                    t.time = later_dt.strftime('%H:%M')
                else:
                    t.time = '23:45'

    def _onchange_breakfast(self):
        for rec in self:
            lines = rec.schedule_line_ids.sorted('sequence')
            transport_lines = rec.transport_line_ids
            if not lines:
                continue
            first_transport = transport_lines[0]
            try:
                dt_transport = datetime.strptime(first_transport.time, '%H:%M')
            except (ValueError, TypeError):
                continue
            # subtract or add 30 minutes
            if rec.prehost_breakfast:
                dt_new_transport = dt_transport - timedelta(minutes=60)
            else:
                dt_new_transport = dt_transport + timedelta(minutes=60)
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

            if any(f in vals for f in rec.TRACKED_FIELDS + ['project_id']):
                prev = rec._get_missing_list()
                new = rec._compute_missing_products()
                rec._set_missing_list(new)
                rec._sync_missing_activity_and_chatter(prev, new)

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

    def _collect_coordinators(self):
        """Projeye bağlı ana siparişteki koordinatör isimlerini topla (varsa)."""
        self.ensure_one()
        order = self.project_id.reinvoiced_sale_order_id if self.project_id else False
        if not order:
            return ""
        # Farklı kurulumlar için sağlam toplama
        names = []
        try:
            # Çoğu kurulumda department/role üstünden employee_ids.user_id olur
            emps = order.coordinator_ids.mapped('employee_ids')
            if emps:
                names = [e.name for e in emps if e.name]
            if not names:
                names = [rec.name for rec in order.coordinator_ids if getattr(rec, 'name', False)]
        except Exception:
            pass
        return "-".join(dict.fromkeys(names))  # uniq + sırayı koru

    def _collect_packages(self):
        """Ek paket/opsiyon etiketleri (True olanları)"""
        pkg_map = [
            ('afterparty_service',          'After Party'),
            ('afterparty_ultra',            'After Party Ultra'),
            ('afterparty_shot_service',     'Shot Servisi (After Party)'),
            ('afterparty_sushi',            'Sushi Bar'),
            ('afterparty_more_drinks',      'Daha Fazla Çeşit İçki (After party zamanı)'),
            ('afterparty_fog_laser',        'Sis & Lazer'),
            ('afterparty_bbq_wraps',        'BBQ Wraps'),
            ('photo_video_plus',            'Photo & Video Plus'),
            ('photo_drone',                 'Drone Kamera'),
            ('menu_hot_appetizer_ultra',    'Rocket Shrimp'),
            ('bar_alcohol_service',         'Yabancı İçki Servisi'),
            ('prehost_barney',              'Barney'),
            ('prehost_fred',                'Fred'),
            ('prehost_breakfast',           'Breakfast Service'),
        ]
        out = []
        for f, label in pkg_map:
            if getattr(self, f):
                if f == 'prehost_breakfast' and self.prehost_breakfast_count:
                    out.append(f"{label} (x{int(self.prehost_breakfast_count)})")
                else:
                    out.append(label)
        return out

    def _collect_program(self):
        """Program akışı başlığı ve satırları (schedule_line_ids)."""
        EVENT_TR = {
            'Cocktail': 'Kokteyl', 'Kokteyl':'Kokteyl',
            'Ceremony': 'Seremoni', 'Seremoni':'Seremoni',
            'Dinner': 'Yemek', 'Yemek':'Yemek',
            'Party': 'Eğlence', 'Parti':'Eğlence',
            'After Party': 'After Party', 'After Parti':'After Party',
        }
        lines = []
        for ln in self.schedule_line_ids.sorted('sequence'):
            ev = (ln.event or '').strip()
            ev_tr = EVENT_TR.get(ev, ev or '-')
            tm = (ln.time or '').strip()
            if ev_tr or tm:
                if tm:
                    lines.append(f"➖{ev_tr}:  {tm}")
                else:
                    lines.append(f"➖{ev_tr}")
        # başlıkta 19:30-01:30 gibi göster
        header = (self.start_end_time or '').replace(' ', '')
        return header, lines

    def _collect_transports(self):
        """Tekne/ulaşım satırları (transport_line_ids)."""
        out = []
        for i, t in enumerate(self.transport_line_ids.sorted('sequence'), start=1):
            label = (t.label or '').strip()
            tm = (t.time or '').strip()
            ports = ', '.join(p.name for p in t.port_ids) if t.port_ids else (t.other_port or '')
            suffix = f" {ports}" if ports else ""
            line = f"{i}/ {label}: {tm}{suffix}".rstrip()
            out.append(line)
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
        tag = getattr(self.table_tag_ids, 'name', '') or ''  # Many2one

        cake = names(self.cake_choice_ids)
        cake_bits = []
        if self.cake_real:
            cake_bits.append("Gerçek Pasta")
        if self.cake_champagne_tower:
            cake_bits.append("Şampanya Kulesi")
        if cake:
            cake_bits.insert(0, cake)
        cake_txt = ', '.join(cake_bits)

        flower = ("Taze" if self.table_fresh_flowers else "") or ("Kuru" if self.table_dried_flowers else "")
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
        if self.music_live:        bits.append("Canlı müzik")
        if self.music_percussion:  bits.append("Perküsyon")
        if self.music_trio:        bits.append("Trio")
        if self.afterparty_service and self.afterparty_ultra:
            bits.append("After Party Ultra var")
        elif self.afterparty_service:
            bits.append("After Party var")
        if self.afterparty_bbq_wraps: bits.append("BBQ Wraps")
        if self.afterparty_fog_laser: bits.append("Sis & Laser")
        if self.afterparty_sushi:     bits.append("Sushi")
        if self.local_music:          bits.append("Yöresel şarkılar planlandı")
        if self.music_other and self.music_other_details:
            bits.append(f"Özel: {self.music_other_details}")
        if self.cocktail_request:
            bits.append("Kokteyl istek listesi mevcut")
        if self.dinner_request:
            bits.append("Yemek istek listesi mevcut")
        if self.party_request:
            bits.append("Parti istek listesi mevcut")
        if self.afterparty_request:
            bits.append("After Party istek listesi mevcut")
        if self.ban_songs:
            bits.append("Yasaklı şarkı listesi mevcut")

        out = []
        if bits:
            out.append("▶️ " + ", ".join(bits) + ".")
        return out

    def _collect_general_notes(self):
        """Genel notlar: nikah/seremoni/konaklama vb. + özel notlar."""
        CEREMONY_MAP = {'actual': 'Gerçek', 'staged': 'Mizansen', 'def': 'Seçili değil'}
        lines = []
        if self.ceremony:
            lines.append(f"➖Nikah : {CEREMONY_MAP.get(self.ceremony, self.ceremony)}")

        if self.accommodation_service:
            acc = self.accommodation_hotel or "Var"
            lines.append(f"➖Konaklama : {acc}")
        other = self._html_to_text(self.other_description)
        addl = self._html_to_text(self.additional_services_description)
        notes = "\n".join(x for x in [other, addl] if x).strip()
        if notes:
            lines.append(notes)
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
        if self.prehost_breakfast:
            cnt = f" (x{int(self.prehost_breakfast_count)})" if self.prehost_breakfast_count else ""
            lines.append(f"➖Kahvaltı Servisi{cnt}")
        if self.bar_alcohol_service:
            # Raki markası (seçiliyse)
            RAKI = dict(self._fields['bar_raki_brand']._description_selection(self.env))
            raki = RAKI.get(self.bar_raki_brand) if self.bar_raki_brand else ""
            lines.append("➖Alkollü içecek servisi" + (f" – {raki}" if raki else ""))
        return lines

    def _display_wedding_type(self):
        # Öncelik: satış şablonunun adı
        if self.sale_template_id and self.sale_template_id.name:
            return self.sale_template_id.name
        # Aksi halde selection label
        try:
            MP = dict(self._fields['wedding_type']._description_selection(self.env))
            return MP.get(self.wedding_type) or ""
        except Exception:
            return self.wedding_type or ""

    def _display_dj(self):
        DJ_MAP = {'engin': 'Engin', 'fatih': 'Fatih', 'other': 'Diğer'}
        return DJ_MAP.get(self.dj_person) or ("Diğer" if self.music_other else "")

    def _build_whatsapp_message(self):
        self.ensure_one()

        tarih = self._format_date_tr(self.invitation_date or self.demo_date)
        tip = self._display_wedding_type() or "-"
        guest = f"{int(self.guest_count)} misafir" if self.guest_count else "-"
        expected = "-"  # Ayrı alan varsa bağlayın
        koordinatör = self._collect_coordinators() or "-"
        dj = self._display_dj() or "-"

        # Ek paketler, program, ulașım, notlar
        packages = self._collect_packages()
        program_header, program_lines = self._collect_program()
        transport_lines = self._collect_transports()
        genel = self._collect_general_notes()
        dekor = self._collect_decor_notes()
        muzik = self._collect_music_notes()
        ikram = self._collect_treats()

        # Yardımcılar
        def ul(items):
            items = [i for i in (items or []) if (i or "").strip()]
            if not items:
                return "<ul><li>-</li></ul>"
            return "<ul>" + "".join(f"<li>{E(i)}</li>" for i in items) + "</ul>"

        def ol(items):
            items = [i for i in (items or []) if (i or "").strip()]
            if not items:
                return ""
            return "<ol>" + "".join(f"<li>{E(i)}</li>" for i in items) + "</ol>"

        def nl2br(s):
            return E(s).replace("\n", "<br>") if s else ""

        other_all = "\n".join(filter(None, [
            getattr(self, "special_notes", "") or "",
            getattr(self, "other_music_notes", "") or "",
        ])).strip()
        other_all=self._html_to_text(other_all)

        html = f"""
        <div>
          <p>🏁 <b>Tarih:</b> {E(tarih)}</p>
          <p>👩</p>
          <p>🔳 <b>Düğün Tipi:</b> {E(tip)}</p>
          <p>🟡 <b>Kişi sayısı:</b> {E(guest)}</p>
          <p>🟢 <b>Beklenen:</b> {E(expected)}</p>
          <p>👧 <b>Koordinatör:</b> {E(koordinatör or "-")}</p>
          <p>🎧 <b>DJ:</b> {E(dj)}</p>
    
          <h4>➕ Ek Paketler:</h4>
          {ul(packages or ["*"])}
    
          <h4>🕖 Program Akışı{f": {E(program_header)}" if program_header else ""}</h4>
          {ul(program_lines)}
    
          <h4>⚓️ Tekne Saatleri:</h4>
          {ol(transport_lines)}
    
          <h4>🔴 Genel Notlar:</h4>
          {ul(genel)}
    
          <h4>⚜️ Dekor Notları:</h4>
          {ul(dekor)}
    
          <h4>🎶 Eğlence Notları:</h4>
          {ul(muzik)}
    
          <h4>‼️Önemli Notlar:</h4>
          <p>{nl2br(other_all) if other_all else "-"}</p>
    
          <h4>🍭 İkramlar:</h4>
          {ul(ikram)}
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

            # Formu modal olarak aç
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