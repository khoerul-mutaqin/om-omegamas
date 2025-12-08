from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PengobatanAlokasi(models.Model):
    _name = 'pengobatan.alokasi'
    _description = 'Pengobatan alokasi'

    name = fields.Char(string='Deskripsi', compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', string='Nama Karyawan', required=True)
    jatah_pengobatan = fields.Float(string='Jatah')
    berlaku_mulai = fields.Date(string='Berlaku Mulai')
    berlaku_sampai = fields.Date(string='Berlaku Sampai')
    sisa = fields.Float(string='Sisa', compute='_compute_sisa', store=False)

    @api.depends('employee_id', 'berlaku_mulai', 'berlaku_sampai')
    def _compute_name(self):
        for rec in self:
            if rec.employee_id and rec.berlaku_mulai and rec.berlaku_sampai:
                rec.name = f"{rec.employee_id.name} - {rec.berlaku_mulai} - {rec.berlaku_sampai}"
            else:
                rec.name = 'Alokasi Tidak Ditemukan'

    @api.depends('jatah_pengobatan', 'employee_id', 'berlaku_mulai', 'berlaku_sampai')
    def _compute_sisa(self):
        PengobatanKlaim = self.env['pengobatan.klaim']
        for rec in self:
            klaim_terpakai = 0.0
            if rec.employee_id and rec.berlaku_mulai and rec.berlaku_sampai:
                klaims = PengobatanKlaim.search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('state', '=', 'paid'),
                    ('tanggal_klaim', '>=', rec.berlaku_mulai),
                    ('tanggal_klaim', '<=', rec.berlaku_sampai),
                ])
                klaim_terpakai = sum(k.nominal for k in klaims)
            rec.sisa = rec.jatah_pengobatan - klaim_terpakai

    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.employee_id.name} - {rec.berlaku_mulai} - {rec.berlaku_sampai}"
            result.append((rec.id, name))
        return result
    
    @api.constrains('jatah_pengobatan')
    def _check_jatah_pengobatan(self):
        for rec in self:
            if rec.jatah_pengobatan == 0:
                raise ValidationError("Jatah Pengobatan tidak boleh 0.")
