from odoo import models, fields

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    private_street = fields.Char(track_visibility='onchange')
    private_email = fields.Char(track_visibility='onchange')
    npwp = fields.Char(track_visibility='onchange')
    agama = fields.Char(track_visibility='onchange')
    legal_name = fields.Char(track_visibility='onchange')
    lang = fields.Selection(track_visibility='onchange')
    registration_number = fields.Char(track_visibility='onchange')
    disabled = fields.Boolean(track_visibility='onchange')
    l10n_id_kode_ptkp = fields.Selection(
        selection=[
            ('tk0', "TK/0"),
            ('tk1', "TK/1"),
            ('tk2', "TK/2"),
            ('tk3', "TK/3"),
            ('k0', "K/0"),
            ('k1', "K/1"),
            ('k2', "K/2"),
            ('k3', "K/3")
        ],
        string="PTKP Code",
        default="tk0",
        required=True,
        groups="hr.group_hr_user",
        help="Employee's tax category that depends on their marital status and number of children",
        track_visibility='onchange',
    )
    employee_type = fields.Selection(track_visibility='onchange')
    user_id = fields.Many2one(track_visibility='onchange')
    hourly_cost = fields.Monetary(track_visibility='onchange')
    mobility_card = fields.Char(track_visibility='onchange')
    pin = fields.Char(track_visibility='onchange')
    barcode = fields.Char(track_visibility='onchange')
    work_email = fields.Char(track_visibility='onchange')
    mobile_phone = fields.Char(track_visibility='onchange')
    category_ids = fields.Many2many(track_visibility='onchange')
    department_id = fields.Many2one(track_visibility='onchange')
    job_id = fields.Many2one(track_visibility='onchange')
    parent_id = fields.Many2one(track_visibility='onchange')
    next_appraisal_date = fields.Date(track_visibility='onchange')
    address_id = fields.Many2one(track_visibility='onchange')
    work_location_id = fields.Many2one(track_visibility='onchange')
    expense_manager_id = fields.Many2one(track_visibility='onchange')
    leave_manager_id = fields.Many2one(track_visibility='onchange')
    attendance_manager_id = fields.Many2one(track_visibility='onchange')
    resource_calendar_id = fields.Many2one(track_visibility='onchange')
    tz = fields.Selection(track_visibility='onchange')
    job_title = fields.Char(track_visibility='onchange')