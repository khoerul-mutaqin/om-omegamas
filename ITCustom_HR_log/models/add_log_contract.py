from odoo import models, fields

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.contract'
    
    department_id = fields.Many2one(track_visibility='onchange')
    job_id = fields.Many2one(track_visibility='onchange')
    contract_type_id = fields.Many2one(track_visibility='onchange')
    hourly_wage = fields.Monetary(track_visibility='onchange')
    l10n_id_bpjs_jkk = fields.Float(track_visibility='onchange')
    # schedule_pay = fields.Selection(track_visibility='onchange')
    # wage_type = fields.Selection(track_visibility='onchange')
    # work_entry_source = fields.Selection(track_visibility='onchange')
