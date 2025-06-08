from odoo import api, models

class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.model
    def create(self, vals):
        project = super().create(vals)
        default_stage_names = [
            'Mekan Seçimi',
            'Davetli Listesi & Davetiyeler',
            'Tedarikçi & Hizmet Koordinasyonu',
            'Prova & Son Hazırlıklar',
            'Düğün Günü Yönetimi',
        ]
        Stage = self.env['project.task.type']
        for name in default_stage_names:
            Stage.create({
                'name': name,
                'project_ids': [(4, project.id)],
            })
        return project
