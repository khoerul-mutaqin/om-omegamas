# models/hr_salary_attachment.py
from odoo import models, fields, api

class HrSalaryAttachment(models.Model):
    _inherit = 'hr.salary.attachment'

    employee_type = fields.Selection(
        related='employee_ids.employee_type',
        string='Employee Type',
        store=True,
        readonly=True
    )