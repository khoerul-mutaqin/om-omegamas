from odoo import api, models, fields
from odoo.exceptions import ValidationError

class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_type = fields.Selection(
        selection_add=[
            ('staff', 'Staff'),
            ('magang', 'Magang'),
            ('konsultan', 'Konsultan')
        ],
        ondelete={'staff': 'set default', 'magang': 'set default', 'konsultan': 'set default'}
    )
    
    npwp = fields.Char(
    string="NPWP",
    store=True
    )

    agama = fields.Char(
        string="Agama",
        store=True
    )

    mulai_bergabung = fields.Date(
        string="Mulai Bergabung",
        store=True
    )

    @api.constrains('npwp')
    def _check_npwp(self):
        for record in self:
            if record.npwp:
                cleaned_npwp = ''.join(filter(str.isdigit, record.npwp))
                if len(cleaned_npwp) != 16:
                    raise ValidationError("NPWP harus terdiri dari 16 digit angka.")

                # Validasi unik secara manual (jaga-jaga jika SQL constraint belum aktif)
                duplicate = self.env['hr.employee'].search([
                    ('id', '!=', record.id),
                    ('npwp', '=', record.npwp)
                ], limit=1)
                if duplicate:
                    raise ValidationError("NPWP harus unik. Sudah digunakan oleh karyawan lain.")

    _sql_constraints = [
        ('unique_npwp', 'UNIQUE(npwp)', 'NPWP harus unik. Sudah digunakan sebelumnya.')
    ]
    
    def surat_peringatan_action(self):
        # Fungsi ini sengaja dikosongkan untuk sekarang
        pass