from odoo import api, fields, models, _
from odoo.exceptions import UserError,ValidationError

ADDENDUM_NAMES = ['Ek Protokol', 'Extra Protocol']


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_project_true = fields.Boolean(string='Is There Any Project?')
    project_task_ids = fields.One2many(
        'sale.project.task',
        'sale_order_id',
        string='Project Tasks',
    )

    @api.onchange('sale_order_template_id')
    def _onchange_sale_template_task(self):
        if not self.sale_order_template_id:
            self.project_task_ids = [(5, 0, 0)]
            self.is_project_true = False
            return

        new_tasks = []
        for tmpl in self.sale_order_template_id.project_task_ids:
            if tmpl.optional_product_id:
                continue

            new_tasks.append((0, 0, {
                'name': tmpl.name,
                'description': tmpl.description,
                'stage_id': tmpl.stage_id.id,
                'planned_date': tmpl.planned_date,
                'deadline_date': tmpl.deadline_date,
                'date_line': tmpl.date_line,
                'days': tmpl.days,
                'user_ids': [(6, 0, tmpl.user_ids.ids)],
                'email_template_id': tmpl.email_template_id.id,
                'communication_type': tmpl.communication_type,
                'event_date': tmpl.event_date,
            }))

        self.project_task_ids = [(5, 0, 0)] + new_tasks
        self.is_project_true = bool(new_tasks)

    @api.onchange('order_line')
    def _onchange_order_line_task(self):
        for order in self:
            if not order.sale_order_template_id:
                return

            current_products = order.order_line.mapped('product_id')
            template_tasks = order.sale_order_template_id.project_task_ids

            to_remove = order.project_task_ids.filtered(
                lambda t: t.optional_product_id and t.optional_product_id not in current_products
            )
            remove_cmds = [(2, t.id) for t in to_remove]

            preserve = order.project_task_ids.filtered(
                lambda t: t.optional_product_id and t.optional_product_id in current_products
            )
            preserve_cmds = [(4, t.id) for t in preserve]

            preserved_prods = preserve.mapped('optional_product_id')
            to_add = template_tasks.filtered(
                lambda tmpl: tmpl.optional_product_id
                             and tmpl.optional_product_id in current_products
                             and tmpl.optional_product_id not in preserved_prods
            )
            add_cmds = []
            for tmpl in to_add:
                add_cmds.append((0, 0, {
                    'name': tmpl.name,
                    'description': tmpl.description,
                    'stage_id': tmpl.stage_id.id,
                    'planned_date': tmpl.planned_date,
                    'deadline_date': tmpl.deadline_date,
                    'date_line': tmpl.date_line,
                    'days': tmpl.days,
                    'user_ids': [(6, 0, tmpl.user_ids.ids)],
                    'email_template_id': tmpl.email_template_id.id,
                    'optional_product_id': tmpl.optional_product_id.id,
                    'communication_type': tmpl.communication_type,
                    'event_date': tmpl.event_date,
                }))

            order.project_task_ids = remove_cmds + preserve_cmds + add_cmds
            order.project_task_ids._onchange_deadline_date()

    def action_open_project_wizard(self):
        self.ensure_one()
        if self.opportunity_id.stage_id.name not in ('Won', 'Kazanıldı'):
            raise UserError(_('Fırsat kazanıldı olmadan proje oluşturamazsın.'))
        if not self.project_task_ids:
            raise UserError(_('Görev girmeden proje oluşturamazsın..'))

        return {
            'name': 'Proje Oluştur',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.project.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,

            },
        }

    def _should_open_extra_protocol_wizard_on_confirm(self):
        """Ek Protokol siparişini onaylarken wizard açalım mı?"""
        self.ensure_one()
        tmpl = (self.sale_order_template_id.name or '').strip().lower()
        return (
            tmpl == 'ek protokol'
            and self.opportunity_id
            and self.opportunity_id.project_id
            and not self.project_id
        )

    def _action_open_update_tasks_wizard_from_confirm(self):
        """Confirm akışından wizard'ı açacak action dict."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Görevleri Güncelle"),
            'res_model': 'sale.order.update.tasks.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'confirm_sale_on_wizard_ok': True,
            }
        }

    def action_confirm(self):

        res = super().action_confirm()
        for order in self:
            if order.sale_order_template_id.name.lower() in ['ek protokol', 'extra protocol']:
                if not order.confirmed_contract:
                    raise UserError(_("Kontrat olmadan satışı onaylayamazsınız."))
                if not order.confirmed_date:
                    raise UserError(_("Kontrat tarihi olmadan satışı onaylayamazsınız."))

        if not self.env.context.get('skip_extra_protocol_on_confirm'):
            for order in self:
                if order.sale_order_template_id.name.lower()=='ek protokol':
                    return order._action_open_update_tasks_wizard_from_confirm()

        return res

    @api.onchange('wedding_date')
    def _onchange_wedding_date(self):
        for rec in self:
            if rec.project_task_ids:
                rec.project_task_ids._onchange_deadline_date()


    def _get_existing_order_in_same_opportunity(self):
        """Aynı fırsattaki (cancel hariç) mevcut siparişlerden birini getirir.
        Genelde tek olduğundan bu yeterli."""
        self.ensure_one()
        if not self.opportunity_id:
            return self.env['sale.order']
        domain = [
            ('opportunity_id', '=', self.opportunity_id.id),
            ('id', '!=', self.id or 0),
            ('state', 'in', ['sale','done']),
        ]
        return self.env['sale.order'].search(domain, order='create_date desc, id desc', limit=1)

    def _get_addendum_template_ids(self):
        Template = self.env['sale.order.template']
        dom = ['|', ('name', 'ilike', ADDENDUM_NAMES[0]), ('name', 'ilike', ADDENDUM_NAMES[1])]
        return set(Template.search(dom).ids)

    def _ensure_template_policy(self, candidate_template_id):
        """Mevcut fırsatta zaten bir satış varsa,
        candidate_template_id yalnızca:
          - önceki satışın template'i
          - veya 'Ek Protokol' / 'Extra Protocol'
        olabilir. Değilse ValidationError fırlatır."""
        self.ensure_one()
        existing = self._get_existing_order_in_same_opportunity()
        if not existing:
            return

        prev_tmpl_id = existing.sale_order_template_id.id or False
        addendum_ids = self._get_addendum_template_ids()

        allowed_ids = set(addendum_ids)
        if prev_tmpl_id:
            allowed_ids.add(prev_tmpl_id)

        if not candidate_template_id and not prev_tmpl_id:
            return

        if candidate_template_id not in allowed_ids:
            addendum_names = ', '.join(
                self.env['sale.order.template'].browse(list(addendum_ids)).mapped('display_name')
            ) or ', '.join(ADDENDUM_NAMES)

            raise ValidationError(
                "Bu fırsata zaten bir satış bağlı. Yeni satış için yalnızca şu şablonlara izin var:\n"
                f"- Ek protokol şablonları: {addendum_names}"
            )

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order, vals in zip(orders, vals_list):
            if vals.get('opportunity_id') and 'sale_order_template_id' in vals:
                order._ensure_template_policy(vals.get('sale_order_template_id'))
            elif vals.get('opportunity_id'):
                pass
        return orders

    def write(self, vals):
        res = super().write(vals)
        if {'sale_order_template_id', 'opportunity_id'} & set(vals.keys()):
            for order in self:
                order._ensure_template_policy(order.sale_order_template_id.id)
        return res

    @api.onchange('opportunity_id', 'sale_order_template_id')
    def _onchange_template_policy(self):
        if not self.opportunity_id:
            return

        existing = self._get_existing_order_in_same_opportunity()
        if not existing:
            return

        addendum_ids = self._get_addendum_template_ids()
        allowed_ids = set(addendum_ids)
        if existing.sale_order_template_id:
            allowed_ids.add(existing.sale_order_template_id.id)

        res = {'domain': {'sale_order_template_id': [('id', 'in', list(allowed_ids) or [0])]}}
        if self.sale_order_template_id and self.sale_order_template_id.id not in allowed_ids:
            prev_name = existing.sale_order_template_id.display_name or '—'
            addendum_names = ', '.join(
                self.env['sale.order.template'].browse(list(addendum_ids)).mapped('display_name')
            ) or ', '.join(ADDENDUM_NAMES)
            res['warning'] = {
                'title': "Şablon Kısıtı",
                'message': (
                    "Bu fırsatta zaten bir satış var. Yeni satış yalnızca şu şablonlarla açılabilir:\n"
                    f"- Önceki satışın şablonu: {prev_name}\n"
                    f"- Ek protokol şablonları: {addendum_names}"
                )
            }
        return res



class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    def add_option_to_order(self):
        order_line = super(SaleOrderOption, self).add_option_to_order()
        self.order_id._onchange_order_line_task()
        return order_line
