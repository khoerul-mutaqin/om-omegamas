# models/hr_contract.py
from odoo import models, fields, api

class HrContract(models.Model):
    _inherit = 'hr.contract'

    employee_type = fields.Selection(
        related='employee_id.employee_type',
        string='Employee Type',
        store=True,
        readonly=True
    )