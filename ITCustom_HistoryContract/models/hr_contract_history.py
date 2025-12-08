# /Users/admin/Documents/odoo-18E/omegamas/ITCustom_HistoryContract/models/hr_contract_history.py
from odoo import models, fields, api

class ContractHistoryConfirmationWizard(models.TransientModel):
    _name = 'contract.history.confirmation.wizard'
    _description = 'Contract History Confirmation Wizard'
    
    contract_id = fields.Many2one('hr.contract', string="Contract", required=True)

    def action_confirm(self):
        self.contract_id._create_history_record()
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}