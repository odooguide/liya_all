from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError,RedirectWarning,UserError
from lxml import html as lhtml
from odoo.tools import html2plaintext, plaintext2html
import re
import json
from html import escape as E


TIME_PATTERN = re.compile(r'(\d{1,2}):([0-5]\d)')
DEFAULT_MEZE_NOTE = (
    'Standart mezelere ilave olarak Kayısı Yahnisi, Lakerda ve '
    'Ahtapot soğuk deniz mezeleri de servis edilir.'
)


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
    guest_count = fields.Integer(related='project_id.so_people_count',string="Guest Count")
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
        help="Provide notes or instructions for the Menu page.",
        default=lambda self: self._default_menu_meze_notes()
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
    merasim=fields.Selection([('nostaljik','Nostaljik Kapı'),('yemek','Yemek Sırasında'),('none','Yok')],string='Merasim')

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
        'photo_homesession': ['Ev Çekimi'],
    }
    TRACKED_FIELDS = list(PRODUCT_REQUIREMENTS.keys())

    def _default_menu_meze_notes(self):
        st_id = self.env.context.get('default_sale_template_id')
        if not st_id:
            return False
        template = self.env['sale.order.template'].browse(st_id)
        if (template.name or '').strip().lower() == 'ultra':
            return DEFAULT_MEZE_NOTE
        return False

    @api.onchange('confirmed_demo_form_plan')
    def _onchange_confirmed_contract_security(self):
        for rec in self:
            origin = rec._origin
            if origin.confirmed_demo_form_plan and not self.env.user.has_group('base.group_system'):
                rec.confirmed_demo_form_plan = origin.confirmed_demo_form_plan
                raise UserError(
                    _('Only administrators can modify or delete the Confirmed Demo Form once uploaded.')
                )

    def _get_related_confirmed_sale_orders(self):
        """Bu projenin bağlı olduğu CRM fırsatındaki onaylı (sale/done) siparişler."""
        self.ensure_one()
        base_order = self.project_id and self.project_id.sudo().reinvoiced_sale_order_id
        opp = base_order.sudo().opportunity_id if base_order else False
        if not opp:
            return self.env['sale.order']
        return self.env['sale.order'].sudo().search([
            ('opportunity_id', '=', opp.id),
            ('state', 'in', ('sale', 'done')),
        ])

    def _first_missing_for_changed_fields(self, vals: dict):
        """
        Bu write çağrısında değiştirilen TRACKED_FIELDS içinden,
        *yalnızca True yönüne geçenleri* kontrol eder.
        İlk eksik ürünü (field, label) döndürür; yoksa (None, None).
        """
        self.ensure_one()
        purchased = self._get_purchased_product_names()

        for f in self.TRACKED_FIELDS:
            if f not in vals:
                continue

            new_val = vals[f]
            old_val = getattr(self, f)

            if f == 'photo_harddisk_delivered':
                if not new_val:
                    continue
                if new_val == old_val:
                    continue
                labels = self.PRODUCT_REQUIREMENTS[f].get(new_val, []) or []

            else:
                if not bool(new_val):
                    continue
                if bool(old_val):
                    continue
                labels = self.PRODUCT_REQUIREMENTS[f]

            for lbl in labels:
                if lbl not in purchased:
                    return f, lbl

        return None, None

    def _get_purchased_product_names(self):
        """İlgili sipariş satırlarından ürün adlarını topla."""
        names = set()
        for so in self._get_related_confirmed_sale_orders():
            for l in so.sudo().order_line:
                n = (l.product_id.name or '').strip()
                if n:
                    names.add(n)
        return names

    def _required_labels_for_field(self, field_name, prospective_val=None):
        """Bir alan için beklenen ürün etiket(ler)i; seçim alanı için prospective_val kullanılabilir."""
        mapping = self.PRODUCT_REQUIREMENTS.get(field_name)
        if not mapping:
            return []
        if field_name == 'photo_harddisk_delivered':
            val = prospective_val if prospective_val is not None else getattr(self, field_name)
            return mapping.get(val, []) if val else []
        return mapping

    @api.depends('special_notes')
    def _compute_split_notes(self):
        limit = 300
        for rec in self:
            raw_html = rec.special_notes or ''

            # HTML → düz metin (satır sonları korunur)
            notes = html2plaintext(raw_html or '')

            # Satır sonlarını normalize et, gereksiz boşlukları toparla
            notes = notes.replace('\r\n', '\n').replace('\r', '\n')
            notes = re.sub(r'[ \t\u00A0]+', ' ', notes)  # ardışık boşlukları tek boşluk yap
            notes = re.sub(r'\n{3,}', '\n\n', notes)  # fazla boş satırları azalt
            notes = notes.strip()

            if len(notes) <= limit:
                preview, remaining = notes, ''
            else:
                cut = notes[:limit]
                last_ws = max(cut.rfind(' '), cut.rfind('\n'), cut.rfind('\t'))
                split_at = last_ws if last_ws != -1 else limit
                preview = cut[:split_at]
                remaining = notes[split_at:].lstrip()

            rec.special_notes_preview = plaintext2html(preview)
            rec.special_notes_remaining = plaintext2html(remaining) if remaining else ''


    @api.model
    def create(self, vals):
        if 'name' in vals and vals.get('name') == _('New Demo Form'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'project.demo.form') or vals['name']

        rec = super(ProjectDemoForm, self).create(vals)

        rec._onchange_start_end_time()
        rec._onchange_breakfast()

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

            for t in rec.transport_line_ids.filtered(lambda l: l.label in ['After Party Dönüş','After Parti Dönüş','After Parti Dönüşü']):
                if rec.afterparty_ultra or rec.afterparty_service:
                    t.time = end_str
                else:
                    t.time = ''

            for t in rec.transport_line_ids.filtered(lambda l: l.label == 'Çift Dönüş'):
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

    def write(self, vals):
        if any(rec.confirmed_demo_form_plan for rec in self) and not self.env.user.has_group('base.group_system'):
            raise UserError("Onaylanmış kayıtta değişiklik yapılamaz.")

        if not (self.env.context.get('extra_protocol_confirmed') or
                self.env.context.get('skip_extra_protocol_check')):
            if set(self.TRACKED_FIELDS).intersection(vals.keys()) or 'photo_harddisk_delivered' in vals:
                for rec in self:
                    field_name, missing_label = rec._first_missing_for_changed_fields(vals or {})
                    if missing_label:
                        action_id = self.env.ref('demo_form.action_project_demo_extra_protocol_wizard').id
                        msg = _(
                            "%s ürünü onaylı tekliflerde bulunamadı.\n\nEk Protokol görevi açılsın mı?") % missing_label
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
        order = self.project_id.sudo().reinvoiced_sale_order_id if self.project_id else False
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
        """Program akışı başlığı ve satırları (schedule_line_ids) + satır notları."""
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
        - Satır notlarını alt satırda gösterir.
        - Listenin en altına 'Ertesi gün çift dönüşü:' maddesini ekler (listede yoksa).
        """
        import re
        out = []
        i = 1

        found_next_day = any(
            'ertesi gün çift dönüşü' in (t.label or '').lower()
            for t in self.transport_line_ids
        )

        for t in self.transport_line_ids.sorted('sequence'):
            label = (t.label or '').strip()
            tm = (t.time or '').strip()

            ports = [p.name.strip() for p in t.port_ids] if t.port_ids else []
            other_port = (t.other_port or '').strip()
            if other_port:
                extra = [p.strip() for p in re.split(r'[,\-/;–—·•]+', other_port) if p.strip()]
                for p in extra:
                    if p not in ports:
                        ports.append(p)

            note_html = getattr(t, 'notes', '') or getattr(t, 'note', '') or getattr(t, 'description', '')
            note_txt = self._html_to_text(note_html) if note_html else ''

            is_return = 'dönüş' in label.lower() or 'dönüşü' in label.lower()

            if is_return and len(ports) > 1:
                for p in ports:
                    line = f"{i}/ {label}: {tm} {p}".rstrip()
                    out.append(line)
                    if note_txt:
                        for sub in note_txt.splitlines():
                            s = sub.strip()
                            if s:
                                out.append(f"    • {s}")
                    i += 1
            else:
                suffix = f" {', '.join(ports)}" if ports else ""
                line = f"{i}/ {label}: {tm}{suffix}".rstrip()
                out.append(line)
                if note_txt:
                    for sub in note_txt.splitlines():
                        s = sub.strip()
                        if s:
                            out.append(f"    • {s}")
                i += 1

        if not found_next_day:
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
        self.ensure_one()
        CEREMONY_MAP = {'actual': 'Gerçek', 'staged': 'Mizansen', 'def': 'Seçili değil'}
        lines = []

        if self.ceremony:
            lines.append(f"➖Nikah : {CEREMONY_MAP.get(self.ceremony, self.ceremony)}")

        if self.accommodation_service:
            acc = self.accommodation_hotel or "Var"
            lines.append(f"➖Konaklama : {acc}")

        if self.merasim:
            sel = self.with_context(lang=self.env.user.lang).fields_get(['merasim'])['merasim']['selection']
            merasim_label = dict(sel).get(self.merasim, self.merasim)
            lines.append(f"➖Merasim : {merasim_label}")
        ceremony='VAR' if self.is_ceremony else 'YOK'
        lines.append(f'➖Seramoni Düzeni : {ceremony}')

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
        if self.bar_alcohol_service:
            # Raki markası (seçiliyse)
            RAKI = dict(self._fields['bar_raki_brand']._description_selection(self.env))
            raki = RAKI.get(self.bar_raki_brand) if self.bar_raki_brand else ""
            lines.append("➖Alkollü içecek servisi" + (f" – {raki}" if raki else ""))
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
        """Menü ve Bar notlarını satır listesi olarak döndürür (WhatsApp formatına uygun).
        Not satırları en altta toplanır ve normal alanlarla arasına <br/> eklenir.
        """
        self.ensure_one()
        lines = []  # normal alanlar
        notes = []  # notlar

        # --- Menü ---
        hot_sel = self.with_context(lang=self.env.user.lang).fields_get(['menu_hot_appetizer'])['menu_hot_appetizer'][
            'selection']
        hot_map = dict(hot_sel)

        if self.menu_hot_appetizer:
            hot_label = hot_map.get(self.menu_hot_appetizer, self.menu_hot_appetizer)
            lines.append(f"➖Sıcak Başlangıç : {hot_label}")

        if self.menu_hot_appetizer_ultra:
            lines.append("➖Sıcak Ekstra : Rocket Shrimp")
        if self.prehost_breakfast:
            cnt = f" (x{int(self.prehost_breakfast_count)})" if self.prehost_breakfast_count else ""
            lines.append(f"➖Kahvaltı Servisi - {cnt}")

        def names(m2m):
            return ", ".join(m2m.mapped('name')) if m2m else ""

        if self.menu_meze_ids:
            lines.append(f"➖Mezeler : {names(self.menu_meze_ids)}")

        meze_notes_txt = self._html_to_text(self.menu_meze_notes) if self.menu_meze_notes else ""
        if meze_notes_txt:
            notes.append(f"➖Meze Notu : {meze_notes_txt}")  # NOT → en alta

        if self.menu_dessert_ids:
            lines.append(f"➖Tatlı : {names(self.menu_dessert_ids)}")

        if self.menu_dessert_ultra_ids:
            lines.append(f"➖Ultra Tatlı : {names(self.menu_dessert_ultra_ids)}")

        menu_notes_txt = self._html_to_text(self.menu_description) if self.menu_description else ""
        if menu_notes_txt:
            notes.append(f"➖Menü Notu : {menu_notes_txt}")  # NOT → en alta

        # --- Bar ---
        raki_sel = self.with_context(lang=self.env.user.lang).fields_get(['bar_raki_brand'])['bar_raki_brand'][
            'selection']
        raki_map = dict(raki_sel)

        if self.bar_alcohol_service:
            lines.append("➖Alkollü içecek servisi : Var")
        else:
            lines.append("➖Alkollü içecek servisi : Yok")
            if self.bar_purchase_advice:
                notes.append(f"➖Satın alma önerisi : {self.bar_purchase_advice}")  # NOT → en alta

        if self.bar_raki_brand:
            lines.append(f"➖Rakı Markası : {raki_map.get(self.bar_raki_brand, self.bar_raki_brand)}")

        bar_notes_txt = self._html_to_text(self.bar_description) if self.bar_description else ""
        if bar_notes_txt:
            notes.append(f"➖Bar Notu : {bar_notes_txt}")  # NOT → en alta

        # --- Ön ev sahibi kahvaltı (F&B) ---
        if getattr(self, "prehost_breakfast", False):
            cnt = f" (x{int(self.prehost_breakfast_count)})" if self.prehost_breakfast_count else ""
            lines.append(f"➖Kahvaltı Servisi{cnt}")

        # --- After Party F&B tek satır ---
        af_items = []
        if getattr(self, "afterparty_shot_service", False):
            af_items.append("Shot Servisi")
        if getattr(self, "afterparty_bbq_wraps", False):
            af_items.append("BBQ Dürümleri")
        if getattr(self, "afterparty_sushi", False) or getattr(self, "afterparty_street_food", False):
            af_items.append("Street Food Atıştırmalık")

        if af_items:
            lines.append("➖After Party : " + ", ".join(af_items))

        if getattr(self, "afterparty_more_drinks", False):
            lines.append("➖After Party İçecekleri : Daha fazla çeşit içki")

        if notes:
            lines.append("")
            lines.extend(notes)

        return lines

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
        mb_lines = self._collect_menu_bar_notes()
        def ul(items):
            items = [i for i in (items or []) if (i or "").strip()]
            ul_style = "list-style:none; margin:0; padding-left:0;"
            li_style = "list-style:none; margin:0; padding:0;"
            if not items:
                return f"<ul style='{ul_style}'><li style='{li_style}'>-</li></ul>"
            lis = "".join(f"<li style='{li_style}'>{E(i)}</li>" for i in items)
            return f"<ul style='{ul_style}'>{lis}</ul>"

        def nl2br(s):
            return E(s).replace("\n", "<br>") if s else ""

        other_all = "\n".join(filter(None, [
            getattr(self, "special_notes", "") or "",
        ])).strip()
        other_all=self._html_to_text(other_all)

        html = f"""
        <div>
          <p>🏁 <b>Tarih:</b> {E(tarih)}</p>
          <p>👩‍❤️‍👨 <b>Çiftimiz:</b> {self.project_id.sudo().reinvoiced_sale_order_id.opportunity_id.name}</p>
          <p>🔳 <b>Düğün Tipi:</b> {E(tip)}</p>
          <p>🟡 <b>Kişi sayısı:</b> {E(guest)}</p>
          <p>🟢 <b>Beklenen:</b> {E(expected)}</p>
          <p>👧 <b>Koordinatör:</b> {E(koordinatör or "-")}</p>
          <p>🎧 <b>DJ:</b> {E(dj)}</p><br/>
    
          <h4>➕ Ek Paketler:</h4>
          {ul(packages or ["*"])}
    
          <h4>🕖 Program Akışı{f": {E(program_header)}" if program_header else ""}</h4>
          {ul(program_lines)}
    
          <h4>⚓️ Tekne Saatleri:</h4>
          {ul(transport_lines)}
    
          <h4>🔴 Genel Notlar:</h4>
          {ul(genel)}
          
    
          <h4>⚜️ Dekor Notları:</h4>
          {ul(dekor)}
          
          <h4>⚜️ Menü ve Bar:</h4>
          {ul(mb_lines)}
          
    
          <h4>🎶 Eğlence Notları:</h4>
          {ul(muzik)}
    
          <h4>‼️Önemli Notlar:</h4>
          <p>{nl2br(other_all) if other_all else "-"}</p>
    
          <h4>🍭 İkramlar:</h4>
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