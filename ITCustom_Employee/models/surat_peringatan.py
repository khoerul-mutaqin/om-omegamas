# /Users/admin/Documents/odoo-18E/omegamas/ITCustom_Employee/models/surat_peringatan.py
from odoo import models, fields

class EmployeeSuratPeringatan(models.Model):
    _name = 'employee.surat.peringatan'
    _description = 'Surat Peringatan Karyawan'

    employee_id = fields.Many2one('hr.employee', string='Karyawan', required=True)
    date_reference = fields.Date(string='Tanggal Referensi', required=True)
    start_date = fields.Date(string='Tanggal Mulai')
    end_date = fields.Date(string='Tanggal Selesai')
    status = fields.Selection([
        ('coaching', 'Coaching'),
        ('sp1', 'Surat Peringatan 1'),
        ('sp2', 'Surat Peringatan 2'),
        ('sp3', 'Surat Peringatan 3'),
        ('teguran', 'Surat Teguran Tertulis'),
        ('skorsing', 'Surat Skorsing')
    ], string='Status', required=True)
    keterangan = fields.Text(string='Keterangan')
