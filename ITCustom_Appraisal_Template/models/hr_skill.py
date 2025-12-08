from odoo import models, fields

class HrSkill(models.Model):
    _inherit = 'hr.skill'
    
    definisi = fields.Text(
        string='Definisi',
        help='Keterangan atau definisi dari skill ini'
    )
