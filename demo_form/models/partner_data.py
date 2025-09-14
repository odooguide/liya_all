from odoo import api, fields, models

class WeddingTrio(models.Model):
    _name = 'wedding.trio'
    _description = 'Wedding Trio'

    name = fields.Char(string='Name', required=True)
    time = fields.Char(string='Time')
    date = fields.Date(string='Event Date')
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    port_ids = fields.Many2many(
        'project.transport.port',
        'wedding_trio_port_rel',
        'trio_id',
        'port_id',
        string='Ports',
    )
    demo_id = fields.Many2one(
        'project.demo.form', string='Demo Formu',
        ondelete='cascade', index=True
    )

class BlueMarmara(models.Model):
    _name = 'blue.marmara'
    _description = 'Blue Marmara'

    name = fields.Char(string='Name', required=True)
    guest_count = fields.Char(string='Guest Count')
    date = fields.Date(string='Event Date')
    boat = fields.Char(string="Boat")
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    demo_id = fields.Many2one(
        'project.demo.form', string='Demo Formu',
        ondelete='cascade', index=True
    )

class PartnerVedans(models.Model):
    _name = 'partner.vedans'
    _description = 'Partner Vedans'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Event Date')
    opportunity_name=fields.Char(string='Isim')
    first_name=fields.Char(string='First Contact')
    second_name=fields.Char(string='Second Contact')
    first_phone = fields.Char(string='First Phone')
    second_phone = fields.Char(string='Second Phone')
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    demo_id = fields.Many2one(
        'project.demo.form', string='Demo Formu',
        ondelete='cascade', index=True
    )
class Studio345(models.Model):
    _name = 'studio.345'
    _description = 'Studio 345'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Tarih')
    opportunity_name=fields.Char(string='İsim')
    first_name=fields.Char(string='First Contact')
    second_name=fields.Char(string='Second Contact')
    first_phone = fields.Char(string='Birincil Telefon')
    second_phone = fields.Char(string='İkincil Telefon')
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    demo_id = fields.Many2one(
        'project.demo.form', string='Demo Formu',
        ondelete='cascade', index=True
    )
    photo_studio=fields.Char('Ekip')

class GarageCaddebostan(models.Model):
    _name = 'garage.caddebostan'
    _description = 'Garage Caddebostan'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Tarih')
    opportunity_name=fields.Char(string='İsim')
    first_name=fields.Char(string='First Contact')
    second_name=fields.Char(string='Second Contact')
    first_phone = fields.Char(string='Birincil Telefon')
    second_phone = fields.Char(string='İkincil Telefon')
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    demo_id = fields.Many2one(
        'project.demo.form', string='Demo Formu',
        ondelete='cascade', index=True
    )
    photo_studio=fields.Char('Ekip')

class Backlight(models.Model):
    _name = 'backlight'
    _description = 'backlight'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Tarih')
    opportunity_name=fields.Char(string='İsim')
    first_name=fields.Char(string='First Contact')
    second_name=fields.Char(string='Second Contact')
    first_phone = fields.Char(string='Birincil Telefon')
    second_phone = fields.Char(string='İkincil Telefon')
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    demo_id = fields.Many2one(
        'project.demo.form', string='Demo Formu',
        ondelete='cascade', index=True
    )
    first_mail = fields.Char(string='Birincil Mail')
    second_mail = fields.Char(string='Birincil Mail')
    drone=fields.Char('Drone')
    home_exit=fields.Char('Evden Çıkış')
    photo_service=fields.Char('Photo Service')
    sale_template_name=fields.Char('Package')
    yacht_shoot=fields.Char('Yacht Shoot')
    photo_print_service=fields.Char('Photo Print Service')


class LiveMusic(models.Model):
    _name='live.music'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Tarih')
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
class ConfirmedForm(models.Model):
    _name='confirmed.form'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Tarih')
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    confirmed_demo_form=fields.Binary(string='Confirmed Demo Form')
    form_name=fields.Char('Form Name')

class DemoMenu(models.Model):
    _name = 'demo.menu'

    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Event Date')
    project_id = fields.Many2one(
        'project.demo.form',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    menu_info=fields.Text(string='Menu Info')

class DemoProjectSharedCompute(models.AbstractModel):
    _name = 'demo.project.shared.compute'
    _description = 'Shared helpers to compute auxiliary O2M rows from Project & Demo'

    @api.model
    def _snapshot(self, rec):
        """rec: project.project veya project.demo.form olabilir."""
        project = rec if rec._name == 'project.project' else rec.project_id
        order = project.sudo().reinvoiced_sale_order_id if project else False
        opp = project.so_opportunity_id if getattr(project, 'so_opportunity_id', False) else (order.sudo().opportunity_id if order else False)
        partner = order.sudo().partner_id if order else False

        event_date = None
        for attr in ('event_date', 'date_start', 'date'):
            v = getattr(project, attr, False)
            if v:
                event_date = fields.Date.to_date(v)
                break
        # gerekirse demodan (invitation/demo_date)
        demo = False
        if project and project.demo_form_ids:
            # onaylı varsa onu, yoksa en yenisini seç
            demo = project.demo_form_ids.sorted('id', reverse=True)[0]
            for df in project.demo_form_ids:
                if getattr(df, 'confirmed_demo_form_plan', False):
                    demo = df
                    break
        if not event_date and demo:
            for attr in ('invitation_date', 'demo_date'):
                v = getattr(demo, attr, False)
                if v:
                    event_date = fields.Date.to_date(v)
                    break

        # satın alınan ürün isimleri ve qty toplamı
        purchased = {}
        if order:
            for l in order.sudo().order_line:
                n = (l.product_id.name or '').strip()
                if n:
                    purchased[n] = purchased.get(n, 0) + int(l.product_uom_qty or 0)

        return {
            'project': project,
            'order': order,
            'opp': opp,
            'partner': partner,
            'event_date': event_date,
            'purchased': purchased,
            'demo': demo,
        }

    # küçük yardımcılar
    @staticmethod
    def _phones_from(project=None, opp=None, partner=None):
        first_name = partner.name if partner else ''
        first_phone = (partner.mobile or partner.phone or '') if partner else ''
        if not first_phone and opp:
            first_phone = (getattr(opp, 'mobile', '') or getattr(opp, 'phone', '') or '')

        second_phone = ''
        second_name = ''
        if opp:
            for attr in ('second_phone', 'second_contact_phone', 'x_second_phone', 'x_phone2'):
                v = getattr(opp, attr, '') or ''
                if v:
                    second_phone = v
                    break
            second_name = getattr(opp, 'second_contact', '') or ''
        return first_name, first_phone, second_name, second_phone

    # ---- Wedding Trio ----
    @api.model
    def commands_wedding_trio(self, rec):
        snap = self._snapshot(rec)
        proj, demo = snap['project'], snap['demo']
        cmds = [(5, 0, 0)]

        # trio var mı? (satıştan veya demodan)
        has_trio = any(n in snap['purchased'] for n in (
            'TRIO', 'Trio', 'Canlı Müzik + Perküsyon + TRIO'
        ))
        if demo and getattr(demo, 'music_trio', False):
            has_trio = True
        if not has_trio:
            return cmds

        if demo:
            gg_lines = demo.transport_line_ids.filtered(
                lambda l: (l.label or '').strip().lower() == 'genel geliş'
            )
            for line in gg_lines:
                cmds.append((0, 0, {
                    'name': line.label or 'Genel Geliş',
                    'time': line.time,
                    'date': snap['event_date'],
                    'port_ids': [(6, 0, line.port_ids.ids)],
                    'project_id': proj.id,
                }))
        else:
            cmds.append((0, 0, {
                'name': 'Genel Geliş',
                'time': '',
                'date': snap['event_date'],
                'project_id': proj.id,
            }))
        return cmds

    # ---- Blue Marmara ----
    @api.model
    def commands_blue_marmara(self, rec):
        snap = self._snapshot(rec)
        proj, demo = snap['project'], snap['demo']

        # kişi sayısı: project.so_people_count > demo.guest_count
        gc = 0
        if proj and getattr(proj, 'so_people_count', 0):
            gc = int(proj.so_people_count)
        elif demo and getattr(demo, 'guest_count', 0):
            gc = int(demo.guest_count)

        boat = '36m' if gc > 250 else '25m'
        name_val = (getattr(demo, 'invitation_owner', '') or 'Blue Marmara').strip()

        return [
            (5, 0, 0),
            (0, 0, {
                'name': name_val,
                'guest_count': str(gc),
                'date': snap['event_date'],
                'boat': boat,
                'project_id': proj.id,
            })
        ]

    # ---- Studio 3435 ----
    @api.model
    def commands_studio_3435(self, rec):
        snap = self._snapshot(rec)
        proj, demo, opp, partner = snap['project'], snap['demo'], snap['opp'], snap['partner']
        # sadece seçilmişse/satın alınmışsa
        has_hair = ('Saç & Makyaj' in snap['purchased']) or (demo and getattr(demo, 'hair_studio_3435', False))
        if not has_hair:
            return [(5, 0, 0)]

        couple = (opp.name or '').strip() if opp else ''
        first_name, first_phone, second_name, second_phone = self._phones_from(proj, opp, partner)

        invite_owner = (getattr(demo, 'invitation_owner', '') or '').strip()
        name_val = invite_owner or " - ".join([b for b in [couple, "Studio 3435 Nişantaşı"] if b]) or "Studio 3435"
        studio_name = "Studio 3435 Nişantaşı"

        return [
            (5, 0, 0),
            (0, 0, {
                'name': name_val,
                'date': snap['event_date'],
                'opportunity_name': couple,
                'first_name': first_name,
                'second_name': second_name,
                'first_phone': first_phone,
                'second_phone': second_phone,
                'photo_studio': studio_name,
                'project_id': proj.id,
            })
        ]

    # ---- Garage Caddebostan ----
    @api.model
    def commands_garage_caddebostan(self, rec):
        snap = self._snapshot(rec)
        proj, demo, opp, partner = snap['project'], snap['demo'], snap['opp'], snap['partner']
        has_hair = ('Saç & Makyaj' in snap['purchased']) or (demo and getattr(demo, 'hair_garage_caddebostan', False))
        if not has_hair:
            return [(5, 0, 0)]

        couple = (opp.name or '').strip() if opp else ''
        first_name, first_phone, second_name, second_phone = self._phones_from(proj, opp, partner)

        invite_owner = (getattr(demo, 'invitation_owner', '') or '').strip()
        name_val = invite_owner or " - ".join([b for b in [couple, "Garage Caddebostan"] if b]) or "Garage Caddebostan"
        studio_name = "Garage Caddebostan"

        return [
            (5, 0, 0),
            (0, 0, {
                'name': name_val,
                'date': snap['event_date'],
                'opportunity_name': couple,
                'first_name': first_name,
                'second_name': second_name,
                'first_phone': first_phone,
                'second_phone': second_phone,
                'photo_studio': studio_name,
                'project_id': proj.id,
            })
        ]

    # ---- Partner Vedans (Dans Show) ----
    @api.model
    def commands_partner_vedans(self, rec):
        snap = self._snapshot(rec)
        proj, demo, opp, partner = snap['project'], snap['demo'], snap['opp'], snap['partner']

        has_dance = ('Dans Show' in snap['purchased']) or (demo and getattr(demo, 'afterparty_dance_show', False))
        if not has_dance:
            return [(5, 0, 0)]

        couple = (opp.name or '').strip() if opp else ''
        first_name, first_phone, second_name, second_phone = self._phones_from(proj, opp, partner)

        name_val = (getattr(demo, 'invitation_owner', '') or couple or 'Partner Vedans').strip()

        return [
            (5, 0, 0),
            (0, 0, {
                'name': name_val,
                'date': snap['event_date'],
                'opportunity_name': couple,
                'first_name': first_name,
                'second_name': second_name,
                'first_phone': first_phone,
                'second_phone': second_phone,
                'project_id': proj.id,
            })
        ]

    # ---- Live Music ----
    @api.model
    def commands_live_music(self, rec):
        snap = self._snapshot(rec)
        proj, demo = snap['project'], snap['demo']
        has_live = any(n in snap['purchased'] for n in (
            'Canlı Müzik', 'Canlı Müzik + Perküsyon', 'Canlı Müzik Özel', 'Canlı Müzik + Perküsyon + TRIO'
        )) or (demo and getattr(demo, 'music_live', False))
        if not has_live:
            return [(5, 0, 0)]

        tmpl_name = ''
        if proj and getattr(proj, 'so_sale_template_id', False):
            tmpl_name = proj.so_sale_template_id.name or ''
        elif demo and getattr(demo, 'sale_template_id', False):
            tmpl_name = demo.sale_template_id.name or ''

        return [
            (5, 0, 0),
            (0, 0, {
                'name': tmpl_name or 'Live Music',
                'date': snap['event_date'],
                'project_id': proj.id,
            })
        ]

    # ---- Backlight ----
    @api.model
    def commands_backlight(self, rec):
        snap = self._snapshot(rec)
        proj, demo, opp, partner = snap['project'], snap['demo'], snap['opp'], snap['partner']

        couple_name = (opp.name or '').strip() if opp else ''
        first_name, first_phone, second_name, second_phone = self._phones_from(proj, opp, partner)

        first_mail = (proj.email_from or '').strip() if proj else ''
        second_mail = (getattr(opp, 'second_mail', '') or '').strip() if opp else ''

        # Drone / Home Exit: demo veya satıştan
        drone = 'Var' if (('Drone Kamera' in snap['purchased']) or (demo and getattr(demo, 'photo_drone', False))) else 'Yok'
        home_exit = 'Var' if (('Evden Çıkış Fotoğraf Çekimi' in snap['purchased']) or (demo and getattr(demo, 'home_exit', False))) else 'Yok'

        # Photo service
        photo_service = ''
        if ('Photo & Video Plus' in snap['purchased']) or (demo and getattr(demo, 'photo_video_plus', False)):
            photo_service = 'Photo & Video Plus'
        elif demo and getattr(demo, 'photo_standard', False):
            photo_service = 'Standart Fotoğraf Servisi'

        sale_template_name = ''
        if proj and getattr(proj, 'so_sale_template_id', False):
            sale_template_name = proj.so_sale_template_id.name or ''
        elif demo and getattr(demo, 'sale_template_id', False):
            sale_template_name = demo.sale_template_id.name or ''

        yacht_shoot = 'VAR' if (('Yacht Photo Shoot' in snap['purchased'])
                                or ('Yat Çekimi' in snap['purchased'])
                                or ('Yat Fotoğraf Çekimi' in snap['purchased'])
                                or (demo and getattr(demo, 'photo_yacht_shoot', False))) else 'YOK'

        photo_print_service = 'VAR' if (demo and getattr(demo, 'photo_print_service', False)) else 'YOK'

        invite_owner = (getattr(demo, 'invitation_owner', '') or '').strip()
        name_val = invite_owner or " - ".join([b for b in [couple_name, "Backlight"] if b]) or "Backlight"

        return [
            (5, 0, 0),
            (0, 0, {
                'name': name_val,
                'date': snap['event_date'],
                'opportunity_name': couple_name,
                'first_name': first_name,
                'second_name': second_name,
                'first_phone': first_phone,
                'second_phone': second_phone,
                'first_mail': first_mail,
                'second_mail': second_mail,
                'drone': drone,
                'home_exit': home_exit,
                'photo_service': photo_service,
                'sale_template_name': sale_template_name,
                'yacht_shoot': yacht_shoot,
                'photo_print_service': photo_print_service,
                'project_id': proj.id,
            })
        ]

    # Benzer şekilde: commands_backlight, commands_garage_caddebostan, commands_vedans, commands_live_music ...

