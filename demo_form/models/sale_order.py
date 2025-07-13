from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_project_true = fields.Boolean(string='Is There Any Project?')
    project_task_ids = fields.One2many(
        'sale.project.task',
        'sale_order_id',
        string='Project Tasks',
    )
    
    @api.onchange('sale_order_template_id')
    def _onchange_sale_order_template_id(self):
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
    
    # @api.onchange('order_line')
    # def _onchange_order_line(self):
    #     for order in self:
    #         if not order.sale_order_template_id:
    #             # template yoksa hiçbir değişiklik
    #             return

    #         # 1) Satırdaki aktif ürünler
    #         products = order.order_line.mapped('product_id')

    #         # 2) Mevcut kayıtlardan, hâlâ satırda var olanları koru
    #         preserve = order.project_task_ids.filtered(
    #             lambda task: task.optional_product_id and task.optional_product_id in products
    #         )
    #         preserved_opts = preserve.mapped('optional_product_id')

    #         # 3) Template’den, satırda olup henüz eklenmemiş görevler
    #         to_add = order.sale_order_template_id.project_task_ids.filtered(
    #             lambda tmpl: tmpl.optional_product_id
    #                          and tmpl.optional_product_id in products
    #                          and tmpl.optional_product_id not in preserved_opts
    #         )

    #         # 4) Komut listesi: önce korunan mevcutlar, sonra yeni eklemeler
    #         commands = [(4, task.id) for task in preserve]
    #         for tmpl in to_add:
    #             commands.append((0, 0, {
    #                 'name':                tmpl.name,
    #                 'description':         tmpl.description,
    #                 'stage_id':            tmpl.stage_id.id,
    #                 'planned_date':        tmpl.planned_date,
    #                 'deadline_date':       tmpl.deadline_date,
    #                 'date_line':           tmpl.date_line,
    #                 'days':                tmpl.days,
    #                 'user_ids':            [(6, 0, tmpl.user_ids.ids)],
    #                 'email_template_id':   tmpl.email_template_id.id,
    #                 'optional_product_id': tmpl.optional_product_id.id,
    #                 'communication_type':  tmpl.communication_type,
    #                 'event_date':          tmpl.event_date,
    #             }))

    #         # 5) Uygula: artık silinmesi gerekenler komut listesinde yok
    #         order.project_task_ids = commands

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
    
class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    @api.onchange('is_present')
    def _onchange_is_present(self):
        for option in self:
            # Eğer işaretlendiyse -> görevleri yarat
            if option.is_present:
                # 1) Şablon görevlerinden bu seçeneğe (product_id) bağlı olanları filtrele
                template_tasks = option.order_id.sale_order_template_id.project_task_ids.filtered(
                    lambda t: t.optional_product_id.id == option.product_id.id
                )
                # 2) sale.project.task modeli
                task_model = self.env['sale.project.task']
                for tmpl in template_tasks:
                    # Aynı görev zaten varsa tekrar ekleme
                    exists = task_model.search([
                        ('sale_order_id', '=', option.order_id.id),
                        ('optional_product_id', '=', option.product_id.id),
                        ('name', '=', tmpl.name),
                    ], limit=1)
                    if not exists:
                        task_model.create({
                            'sale_order_id': option.order_id.id,
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
                        })
            else:
                # Eğer işaret kaldırıldıysa -> ilgili sale.project.task kayıtlarını sil
                tasks = self.env['sale.project.task'].search([
                    ('sale_order_id', '=', option.order_id.id),
                    ('optional_product_id', '=', option.product_id.id),
                ])
                tasks.unlink()