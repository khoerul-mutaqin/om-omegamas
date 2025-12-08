# /Users/admin/Documents/odoo-18E/omegamas/ITCustom_HistoryContract/models/hr_contract_history.py
from odoo import models, fields, api

class HrContractHistory(models.Model):
    _name = 'contract.history.employee'
    _description = 'History of HR Contract'

    contract_id = fields.Many2one('hr.contract', string="Contract", required=True)
    history_name = fields.Char(string="History Name")
    history_start_date = fields.Date(string="History Start Date")
    history_end_date = fields.Date(string="History End Date")

    # Tambahan field Many2one dari hr.contract
    history_structure_type_id = fields.Many2one(
        'hr.payroll.structure.type',
        string="Structure Type"
    )

    history_department_id = fields.Many2one(
        'hr.department',
        string="Department"
    )

    history_job_id = fields.Many2one(
        'hr.job',
        string="Job Position"
    )

    status = fields.Selection([
        ('pkwt', 'PKWT'),
        ('perpanjangan_pkwt', 'Perpanjangan PKWT'),
        ('resign', 'Resign'),
        ('habis_kontrak', 'Habis Kontrak'),
        ('permanent', 'Permanent')
    ], string='Status Kontrak')
    
    keterangan = fields.Text(string='Keterangan')