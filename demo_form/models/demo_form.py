from odoo import models, fields

class DemoForm(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'demo.form'
    _description = 'Demo Form'

    name=fields.Char(string="Name")

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Proje',
        ondelete='cascade'
    )
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='demo_form_ir_attachments_rel',
        column1='res_id',
        column2='attachment_id',
        string='Ekli Dosyalar',
        domain=[('res_model', '=', 'demo.form')],
        help='Bu kayda ekli dosyalar.'
    )

    davet_sahibi       = fields.Char(string="Davet Sahibi")
    davet_tarihi       = fields.Date(string="Davet Tarihi")
    gun                = fields.Selection(
        [
            ('pazartesi','Pazartesi'),
            ('sali','Salı'),
            ('carsamba','Çarşamba'),
            ('persembe','Perşembe'),
            ('cuma','Cuma'),
            ('cumartesi','Cumartesi'),
            ('pazar','Pazar'),
        ], string="Gün"
    )
    dugun_tipi         = fields.Selection(
        [
            ('mini','Mini'),
            ('all_in_one','All-In-One'),
            ('premium','Premium'),
        ], string="Düğün Tipi"
    )
    kisi_sayisi        = fields.Integer(string="Kişi Sayısı")
    nikah_tipi         = fields.Selection(
        [
            ('gercek','Gerçek'),
            ('mizansen','Mizansen'),
        ], string="Nikah"
    )
    baslangic_saati    = fields.Float(string="Başlangıç Saati", help="Örn. 19.30")
    bitis_saati        = fields.Float(string="Bitiş Saati", help="Örn. 01.30")

    # 2) Demo & Notlar
    demo_tarihi        = fields.Date(string="Demo Tarihi")
    ozel_notlar        = fields.Text(string="Özel Notlar")

    # 3) Saat Akışı (A)
    tekne_kalkis_zamani = fields.Float(string="Tekne Kalkış Zamanı")
    tekne_kalkis_not    = fields.Char(string="Tekne Kalkış Açıklama")
    kokteyl_zamani      = fields.Float(string="Kokteyl Zamanı")
    kokteyl_not         = fields.Char(string="Kokteyl Açıklama")
    nikah_zamani        = fields.Float(string="Nikah Zamanı")
    nikah_mekan         = fields.Selection(
        [
            ('restaurant','Restaurant'),
            ('beach','Beach'),
        ], string="Nikah Mekanı"
    )
    nikah_konusma_var   = fields.Boolean(string="Nikah Konuşması Var mı?")
    nikah_konusma_sure  = fields.Char(string="Konuşma Süresi")
    yemek_zamani        = fields.Float(string="Yemek Zamanı")
    yemek_not           = fields.Char(string="Yemek Açıklama")
    party_zamani        = fields.Float(string="Party Zamanı")
    party_mekan         = fields.Selection(
        [
            ('restaurant','Restaurant'),
            ('beach','Beach'),
        ], string="Party Mekanı"
    )
    afterparty_baslangic = fields.Float(string="After Party Başlangıç")
    afterparty_bitis     = fields.Float(string="After Party Bitiş")

    # 4) Ulaşım (B)
    ulasim_cift_gelis_zamani    = fields.Float(string="Çift Geliş Zamanı")
    ulasim_cift_gelis_liman      = fields.Selection(
        [
            ('dragos','Dragos'),
            ('diger','Diğer'),
        ], string="Liman"
    )
    ulasim_cift_gelis_not_zamani = fields.Float(string="Bilgi Notu Zamanı")
    ulasim_cift_gelis_not        = fields.Char(string="Ulaşım Açıklama")