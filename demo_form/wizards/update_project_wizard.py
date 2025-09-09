from odoo import api, fields, models, _
from datetime import timedelta, date

class SaleOrderUpdateTasksWizard(models.TransientModel):
    _name = 'sale.order.update.tasks.wizard'
    _description = 'Wizard: Existing Project – Add Tasks from Sale Order'

    sale_order_id = fields.Many2one(
        'sale.order', string='Sale Order', required=True, ondelete='cascade'
    )
    project_id = fields.Many2one(
        'project.project', string='Existing Project', readonly=True
    )
    line_ids = fields.One2many(
        'sale.order.update.tasks.wizard.line', 'wizard_id',
        string='Tasks to Add'
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        order_id = self.env.context.get('default_sale_order_id')
        if not order_id:
            return res

        order = self.env['sale.order'].browse(order_id)
        project = order.project_id or order.opportunity_id.project_id
        res['project_id'] = project.id if project else False

        if 'line_ids' in fields_list:
            lines = [
                (0, 0, {
                    'task_id': task.id,
                    'name': task.name,
                    'description': task.description,
                    'stage_id': task.stage_id.id,
                    'planned_date': task.planned_date,
                    'date_line': task.date_line,
                    'days': task.days,
                    'deadline_date': task.deadline_date,
                    'user_ids': task.user_ids.ids,
                    'email_template_id': task.email_template_id.id,
                    'optional_product_id': task.optional_product_id.id,
                    'communication_type': task.communication_type,
                })
                for task in order.project_task_ids
            ]
            res['line_ids'] = lines
        return res

    def action_confirm(self):
        """Mevcut projeye görevleri ekle + varsa demo formu yeni siparişe göre güncelle."""
        self.ensure_one()
        order = self.sale_order_id
        project = self.project_id or order.opportunity_id.project_id
        if not project:
            return {'type': 'ir.actions.act_window_close'}
        order.project_id=order.opportunity_id.project_id
        project.sudo().write({
            'related_sale_order_ids': [(4, order.id)],
        })

        def _resolve_responsibles(tmpl_line):
            if tmpl_line.user_ids:
                return tmpl_line.user_ids.ids
            user_recs = order.coordinator_ids.sudo().mapped('employee_ids.user_id')
            users = self.env['res.users'].sudo().search([('id', 'in', user_recs.ids)])
            return users.ids or [self.env.user.id]

        # LCV alt görevleri
        lcv_subtasks = [
            'Çifte LCV Listesi Paylaş',
            'LCV Listesi çift tarafından dolduruldu',
            'LCV Aranıyor',
            'Raporlandı',
            'Yedek liste',
            'Oturma Planı paylaşıldı',
        ]

        for tmpl in self.line_ids:
            responsibles = _resolve_responsibles(tmpl)

            sale_line = order.order_line.filtered(lambda l: l.product_id == tmpl.optional_product_id)
            sale_line_id = sale_line and sale_line[0].id or False

            new_task = self.env['project.task'].sudo().create({
                'project_id': project.id,
                'name': tmpl.name,
                'description': tmpl.description,
                'stage_id': tmpl.stage_id.id,
                'user_ids': [(6, 0, responsibles)],
                'date_deadline': tmpl.deadline_date,
                'email_template_id': tmpl.email_template_id.id,
                'communication_type': tmpl.communication_type,
                'sale_line_id': sale_line_id,
                'task_tags': tmpl.name,
            })

            if tmpl.communication_type == 'phone' and tmpl.email_template_id:
                template = tmpl.email_template_id
                rendered = template._render_template_qweb(
                    template.body_html, template.model, [new_task.id]
                )
                body = rendered.get(new_task.id) if isinstance(rendered, dict) else rendered
                new_task.message_post(body=body, subtype_xmlid='mail.mt_comment')

            if 'lcv' in (tmpl.name or '').lower():
                for sub_name in lcv_subtasks:
                    self.env['project.task'].create({
                        'project_id': project.id,
                        'name': sub_name,
                        'parent_id': new_task.id,
                        'user_ids': [(6, 0, responsibles)],
                    })

        demo = self.env['project.demo.form'].search([('project_id', '=', project.id)], limit=1)
        vals = {}
        if demo and not demo.confirmed_demo_form_plan:
            for sol in order.order_line:
                pname = (sol.product_id.name or '').strip()
                up = pname.upper()

                if pname == "Photo & Video Plus":
                    vals['photo_video_plus'] = True
                if pname == "Drone Kamera":
                    vals['photo_drone'] = True

                # HDD teslim (Selection)
                if pname == "Hard Disk 1TB Delivered":
                    vals['photo_harddisk_delivered'] = 'delivered'
                if pname == "Will Deliver Later":
                    vals['photo_harddisk_delivered'] = 'later'

                if pname == "After Party":
                    vals['afterparty_service'] = True
                if pname == "After Party Ultra":
                    if demo.afterparty_service or vals.get('afterparty_service'):
                        vals['afterparty_ultra'] = True
                if pname == "After Party Shot Servisi":
                    vals['afterparty_shot_service'] = True
                if pname == "Sushi Bar":
                    vals['afterparty_sushi'] = True
                if pname == "Dans Show":
                    vals['afterparty_dance_show'] = True
                if pname == "Fog + Laser Show":
                    vals['afterparty_fog_laser'] = True

                # Bar
                if pname == "Yabancı İçki Servisi":
                    vals['bar_alcohol_service'] = True

                # Saç & makyaj
                if pname == "Saç & Makyaj":
                    date_str = demo.invitation_date or demo.demo_date
                    if date_str:
                        dt = fields.Date.from_string(date_str)
                        if dt.weekday() in (2, 3, 4, 5):
                            vals['hair_studio_3435'] = True
                        else:
                            vals['hair_garage_caddebostan'] = True

                # Pasta opsiyonları
                if "Pasta Show'da Gerçek Pasta" in pname:
                    vals['cake_real'] = True
                if "Pasta Show'da Şampanya Kulesi" in pname:
                    vals['cake_champagne_tower'] = True


                if up == "BARNEY":
                    vals['prehost_barney'] = True
                if up == "FRED":
                    vals['prehost_fred'] = True
                if pname == "Breakfast Service":
                    vals['prehost_breakfast'] = True
                    vals['prehost_breakfast_count'] = int(sol.product_uom_qty or 0)

        if vals:
            demo.sudo().write(vals)

        order.with_context(skip_extra_protocol_on_confirm=True).action_confirm()
        return {'type': 'ir.actions.act_window_close'}


class SaleOrderUpdateTasksWizardLine(models.TransientModel):
    _name = 'sale.order.update.tasks.wizard.line'
    _description = 'Wizard Line: Tasks to Add into Existing Project'

    wizard_id = fields.Many2one(
        'sale.order.update.tasks.wizard', string='Wizard', required=True, ondelete='cascade'
    )

    task_id = fields.Many2one('sale.project.task', string='Project Template')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order Id')
    name = fields.Char(string='Task Name')
    description = fields.Text(string='Description')
    stage_id = fields.Many2one('project.task.type', string='Stage')

    planned_date = fields.Selection([
        ('before_wedding', 'Before Wedding'),
        ('border', 'Border Date'),
        ('casual_date', 'Stable Date'),
    ], string='Planned Type')

    date_line = fields.Char(string='Border Date Line')
    days = fields.Integer(string='Days')
    deadline_date = fields.Date(string='Deadline Date')

    user_ids = fields.Many2many('res.users', string='Responsibles')
    email_template_id = fields.Many2one('mail.template', string='E-Mail Template')
    optional_product_id = fields.Many2one('product.product', string='Optional Product')
    communication_type = fields.Selection([
        ('mail', 'E-Mail'),
        ('phone', 'Whatsapp'),
    ], string='Communication Type')

    @api.onchange('planned_date', 'days', 'date_line')
    def _onchange_deadline_date(self):
        for rec in self:
            today = fields.Date.today()
            wedding_date = rec.wizard_id.sale_order_id.wedding_date
            if not wedding_date:
                rec.deadline_date = False
                continue

            if rec.planned_date == 'before_wedding':
                rec.deadline_date = (wedding_date - timedelta(days=rec.days)) if rec.days else False

            elif rec.planned_date == 'border':
                if not rec.date_line:
                    rec.deadline_date = False
                    continue
                try:
                    day_str, month_str = rec.date_line.split('.')
                    day, month = int(day_str), int(month_str)
                    base_dt = date(today.year, month, day)
                except Exception:
                    rec.deadline_date = False
                    continue

                same_year = (wedding_date.year == today.year)
                if same_year and wedding_date and wedding_date > base_dt and today > base_dt:
                    target = today + timedelta(days=rec.days or 0)
                else:
                    target = base_dt
                    if target <= today:
                        target = date(today.year + 1, month, day)
                rec.deadline_date = target
            else:
                # casual_date: elle girilecek/sabit – burada otomatik hesap yok
                rec.deadline_date = rec.deadline_date