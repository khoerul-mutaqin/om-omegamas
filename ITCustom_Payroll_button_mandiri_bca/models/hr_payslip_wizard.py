from odoo import models, fields, api

class HrPayslipWizard(models.TransientModel):
    _name = 'hr.payslip.wizard'
    _description = 'Wizard Export Mandiri'

    export_date = fields.Date(string="Tanggal Pembayaran", required=True, default=fields.Date.context_today)

    def action_confirm(self):
        active_ids = self.env.context.get('active_ids', [])
        payslips = self.env['hr.payslip'].browse(active_ids)
        return payslips.export_to_mandiri(self.export_date)
