# models/hr_payslip.py
from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    barcode = fields.Char(related="employee_id.barcode", string="Nomor Karyawan", store=True)
    employee_type = fields.Selection(related="employee_id.employee_type", string="Tipe Karyawan", store=True)
    bank_name = fields.Char(related="employee_id.bank_account_id.bank_id.name", string="Nama Bank", store=True)
    t_alrapel = fields.Monetary(string="(T) Alrapel", compute="_compute_alrapel", store=True, currency_field='currency_id')
    t_makan = fields.Monetary(string="(T) Makan", compute="_compute_t_makan", store=True, currency_field='currency_id')
    t_jkk = fields.Monetary(string="(T) JKK", compute="_compute_t_jkk", store=True, currency_field='currency_id')
    t_jkm = fields.Monetary(string="(T) JKM", compute="_compute_t_jkm", store=True, currency_field='currency_id')
    t_jht_comp = fields.Monetary(string="(T) JHT Comp", compute="_compute_t_jht_comp", store=True, currency_field='currency_id')
    t_bpjs_kesehatan = fields.Monetary(string="(T) BPJS Kesehatan", compute="_compute_t_bpjs_kesehatan", store=True, currency_field='currency_id')
    t_jp_company = fields.Monetary(string="(T) JP Company", compute="_compute_t_jp_company", store=True, currency_field='currency_id')
    t_jabatan = fields.Monetary(string="(T) Jabatan", compute="_compute_t_jabatan", store=True, currency_field='currency_id')
    t_tidak_tetap = fields.Monetary(string="(T) Tidak Tetap", compute="_compute_t_tidak_tetap", store=True, currency_field='currency_id')
    t_pencairan_pinjaman = fields.Monetary(string="Pencairan Pinjaman", compute="_compute_pencairan_pinjaman", store=True, currency_field='currency_id')
    t_lain_lain = fields.Monetary(string="(T) Lain Lain", compute="_compute_t_lain_lain", store=True, currency_field='currency_id')
    t_insentif = fields.Monetary(string="(T) Insentif", compute="_compute_t_insentif", store=True, currency_field='currency_id')
    t_pph21 = fields.Monetary(string="(T) PPH21", compute="_compute_t_pph21", store=True, currency_field='currency_id')
    sub_gross = fields.Monetary(string="SUB GROSS", compute="_compute_sub_gross", store=True, currency_field='currency_id')
    p_jht_comp = fields.Monetary(string="(P) JHT Comp", compute="_compute_p_jht_comp", store=True, currency_field='currency_id')
    p_jht_employee = fields.Monetary(string="(P) JHT Employee", compute="_compute_p_jht_employee", store=True, currency_field='currency_id')
    p_bpjs_jkk = fields.Monetary(string="(P) BPJS JKK", compute="_compute_p_bpjs_jkk", store=True, currency_field='currency_id')
    p_bpjs_jkm = fields.Monetary(string="(P) BPJS JKM", compute="_compute_p_bpjs_jkm", store=True, currency_field='currency_id')
    p_bpjs_kes_comp = fields.Monetary(string="(P) BPJS Kes Comp", compute="_compute_p_bpjs_kes_comp", store=True, currency_field='currency_id')
    p_bpjs_kes_emp = fields.Monetary(string="(P) BPJS Kes Emp", compute="_compute_p_bpjs_kes_emp", store=True, currency_field='currency_id')
    p_jp_company = fields.Monetary(string="(P) JP Company", compute="_compute_p_jp_company", store=True, currency_field='currency_id')
    p_jp_employee = fields.Monetary(string="(P) JP Employee", compute="_compute_p_jp_employee", store=True, currency_field='currency_id')
    p_meal = fields.Monetary(string="(P) Meal", compute="_compute_p_meal", store=True, currency_field='currency_id')
    p_pph21 = fields.Monetary(string="(P) PPH21", compute="_compute_p_pph21", store=True, currency_field='currency_id')
    p_tunj_tidak_tetap = fields.Monetary(string="(P) Tunj. Tidak Tetap", compute="_compute_p_tunj_tidak_tetap", store=True, currency_field='currency_id')
    p_absensi = fields.Monetary(string="(P) Absensi", compute="_compute_p_absensi", store=True, currency_field='currency_id')
    p_terlambat = fields.Monetary(string="(P) Terlambat", compute="_compute_p_terlambat", store=True, currency_field='currency_id')
    p_pd = fields.Monetary(string="(P) Pulang Dini", compute="_compute_p_pd", store=True, currency_field='currency_id')
    p_mp = fields.Monetary(string="(P) Meninggalkan Pekerjaan", compute="_compute_p_mp", store=True, currency_field='currency_id')
    p_pinjaman = fields.Monetary(string="(P) Pinjaman", compute="_compute_pinjaman", store=True, currency_field='currency_id')
    p_gaji = fields.Monetary(string="(P) Potong Gaji", compute="_compute_potong_gaji", store=True, currency_field='currency_id')
    p_potongan = fields.Monetary(string="Total Potongan", compute="_compute_potongan", store=True, currency_field='currency_id')

    
    @api.depends('line_ids.total')
    def _compute_alrapel(self):
        for record in self:
            payslip_line = self.env['hr.payslip.line'].search([
                ('slip_id', '=', record.id),
                ('code', '=', 'ALRAPEL')
            ], limit=1)
            record.t_alrapel = payslip_line.total if payslip_line else 0.0

    @api.depends('line_ids.total')
    def _compute_t_makan(self):
        for record in self:
            payslip_line = self.env['hr.payslip.line'].search([
                ('slip_id', '=', record.id),
                ('code', '=', 'MA')
            ], limit=1)
            record.t_makan = payslip_line.total if payslip_line else 0.0
            
    @api.depends('line_ids.total')
    def _compute_pencairan_pinjaman(self):
        for record in self:
            payslip_line = self.env['hr.payslip.line'].search([
                ('slip_id', '=', record.id),
                ('code', '=', 'PENPINJAMAN')
            ], limit=1)
            record.t_pencairan_pinjaman = payslip_line.total if payslip_line else 0.0
            
    @api.depends('line_ids.total')
    def _compute_t_jkk(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'BPJS_JKK')
            record.t_jkk = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_t_jkm(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'BPJS_JKM')
            record.t_jkm = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_t_jht_comp(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'JHTC+')
            record.t_jht_comp = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_t_bpjs_kesehatan(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'BPJS_Kesehatan')
            record.t_bpjs_kesehatan = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_t_jp_company(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'JPC+')
            record.t_jp_company = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_t_jabatan(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'TJ')
            record.t_jabatan = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_t_tidak_tetap(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'TTT')
            record.t_tidak_tetap = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_t_lain_lain(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'TLL')
            record.t_lain_lain = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_t_insentif(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'INS')
            record.t_insentif = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_sub_gross(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'SUBGROSS')
            record.sub_gross = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_t_pph21(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'PPH21ALW')
            record.t_pph21 = line.total if line else 0.0
            
    @api.depends('line_ids.total')
    def _compute_p_jht_comp(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'JHTC-')
            record.p_jht_comp = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_p_jht_employee(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'JHTEmployee')
            record.p_jht_employee = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_p_bpjs_jkk(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'BPJS_JKK-')
            record.p_bpjs_jkk = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_p_bpjs_jkm(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'BPJS_JKM-')
            record.p_bpjs_jkm = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_p_bpjs_kes_comp(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'BPJS_Kesehatan-')
            record.p_bpjs_kes_comp = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_p_bpjs_kes_emp(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'BPJS_KES_EMPLOYEE-')
            record.p_bpjs_kes_emp = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_p_jp_company(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'JPC')
            record.p_jp_company = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_p_jp_employee(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'JPE')
            record.p_jp_employee = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_p_meal(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'PM')
            record.p_meal = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_p_pph21(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'PPH21DED')
            record.p_pph21 = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_p_tunj_tidak_tetap(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'PTTT')
            record.p_tunj_tidak_tetap = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_p_absensi(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'PABS')
            record.p_absensi = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_p_terlambat(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'TLB')
            record.p_terlambat = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_p_pd(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'PPD')
            record.p_pd = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_p_mp(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'MP')
            record.p_mp = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_pinjaman(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'PINJAMAN')
            record.p_pinjaman = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_potong_gaji(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'PG')
            record.p_gaji = line.total if line else 0.0

    @api.depends('line_ids.total')
    def _compute_potongan(self):
        for record in self:
            line = record.line_ids.filtered(lambda l: l.code == 'POTONGAN')
            record.p_potongan = line.total if line else 0.0
