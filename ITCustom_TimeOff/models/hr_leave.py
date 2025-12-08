from odoo import models, fields

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    employee_type = fields.Selection(
        related='employee_id.employee_type',
        string='Employee Type',
        store=True,
        readonly=True
    )
