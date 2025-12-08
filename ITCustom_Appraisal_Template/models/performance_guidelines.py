from odoo import models, fields, api

class PerformanceGuidelines(models.Model):
    _name = 'performance.guidelines'
    _description = 'Performance Evaluation Guidelines'
    _order = 'sequence, id'

    sequence = fields.Integer('Sequence', default=10)
    template_id_umum = fields.Many2one(
        'appraisal.template', 
        string='Appraisal Template Umum', 
        ondelete='cascade'
    )
    template_id_khusus = fields.Many2one(
        'appraisal.template', 
        string='Appraisal Template Khusus', 
        ondelete='cascade'
    )
    template_id_kepemimpinan = fields.Many2one(
        'appraisal.template', 
        string='Appraisal Template Kepemimpinan', 
        ondelete='cascade'
    )
    factor = fields.Char('Faktor Perilaku Kerja', required=True)
    definition = fields.Text('Definisi')
    value_1 = fields.Text('NILAI 20% (Kurang Diterima)')
    value_2 = fields.Text('NILAI 40% (Butuh Arahan)')
    value_3 = fields.Text('NILAI 60% (Standart)')
    value_4 = fields.Text('NILAI 80% (Performa Bagus)')
    value_5 = fields.Text('NILAI 100% (Luar Biasa)')
