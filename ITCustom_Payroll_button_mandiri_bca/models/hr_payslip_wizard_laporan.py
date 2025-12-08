from odoo import models, fields, api

class HrPayslipWizard(models.TransientModel):
    _name = 'hr.payslip.wizard.laporan'
    _description = 'Wizard Export Laporan'

    export_date = fields.Date(string="Tanggal Pembayaran", required=True, default=fields.Date.context_today)
    export_type = fields.Selection([
        ('excel', 'Excel'),
        ('pdf', 'PDF')
    ], string="Jenis File", required=True, default='excel')
    tunjangan_fields = fields.Many2many(
        'ir.model.fields',
        'hr_payslip_wizard_tunjangan_rel',
        string="Tunjangan",
        domain=[('model', '=', 'hr.payslip'), ('name', 'in', [
            't_alrapel', 
            't_jkm', 
            't_jkk', 
            't_jht_comp', 
            't_bpjs_kesehatan',
            't_jp_company', 
            't_tidak_tetap', 
            't_pencairan_pinjaman',
            't_lain_lain', 
            't_jabatan', 
            't_insentif', 
            't_makan', 
            't_pph21'
        ])],
        default=lambda self: self.env['ir.model.fields'].search([
            ('model', '=', 'hr.payslip'),
            ('name', 'in', [
            't_alrapel', 
            't_jkm', 
            't_jkk', 
            't_jht_comp', 
            't_bpjs_kesehatan',
            't_jp_company', 
            't_tidak_tetap', 
            't_pencairan_pinjaman',
            't_lain_lain', 
            't_jabatan', 
            't_insentif', 
            't_makan', 
            't_pph21'
            ])
        ])
    )
    potongan_fields = fields.Many2many(
        'ir.model.fields',
        'hr_payslip_wizard_potongan_rel',
        string="Potongan",
        domain=[('model', '=', 'hr.payslip'), ('name', 'in', [
            'p_bpjs_jkk', 
            'p_bpjs_jkm', 
            'p_jht_employee', 
            'p_jht_comp', 
            'p_bpjs_kes_comp',
            'p_bpjs_kes_emp', 
            'p_jp_company', 
            'p_jp_employee', 
            'p_meal', 
            'p_terlambat', 
            'p_pd', 
            'p_mp', 
            'p_pinjaman', 
            'p_tunj_tidak_tetap', 
            'p_gaji',
            'p_absensi', 
            'p_pph21',
        ])],
        default=lambda self: self.env['ir.model.fields'].search([
            ('model', '=', 'hr.payslip'),
            ('name', 'in', [
            'p_bpjs_jkk', 
            'p_bpjs_jkm', 
            'p_jht_employee', 
            'p_jht_comp', 
            'p_bpjs_kes_comp',
            'p_bpjs_kes_emp', 
            'p_jp_company', 
            'p_jp_employee', 
            'p_meal', 
            'p_terlambat', 
            'p_pd', 
            'p_mp', 
            'p_pinjaman', 
            'p_tunj_tidak_tetap', 
            'p_gaji',
            'p_absensi', 
            'p_pph21',
            ])
        ])
    )

    def action_confirm(self):
        active_ids = self.env.context.get('active_ids', [])
        payslips = self.env['hr.payslip'].browse(active_ids)
        export_date = self.export_date
        export_type = self.export_type
        selected_field_names = self.tunjangan_fields.mapped('name') + self.potongan_fields.mapped('name')

        if export_type == 'excel':
            return payslips.export_to_laporan(export_date, selected_field_names)
        elif export_type == 'pdf':
            return payslips.export_to_laporan_pdf(export_date, selected_field_names)