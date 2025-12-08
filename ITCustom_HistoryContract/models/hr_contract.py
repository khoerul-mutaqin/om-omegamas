# /Users/admin/Documents/odoo-18E/omegamas/ITCustom_HistoryContract/models/hr_contract.py
from odoo import models, fields, api

class HrContract(models.Model):
    _inherit = 'hr.contract'

    history_ids = fields.One2many(
        'contract.history.employee',  # related model
        'contract_id',                # field di model tujuan (Many2one)
        string='History Records'
    )
    
    def action_update_history(self):
        return {
            'name': 'Konfirmasi Update Riwayat',
            'type': 'ir.actions.act_window',
            'res_model': 'contract.history.confirmation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_contract_id': self.id,
            }
        }
    
    def _create_history_record(self):
        """Internal method to create history record"""
        self.ensure_one()
        # Ambil riwayat terakhir berdasarkan create_date (atau id, fallback)
        last_history = self.env['contract.history.employee'].search(
            [('contract_id', '=', self.id)],
            order='create_date desc',  # Bisa juga 'id desc'
            limit=1
        )

        # Ambil data kontrak saat ini
        current_data = {
            'history_name': self.name,
            'history_start_date': self.date_start,
            'history_end_date': self.date_end,
            'history_structure_type_id': self.structure_type_id.id,
            'history_department_id': self.department_id.id,
            'history_job_id': self.job_id.id,
        }

        is_different = True  # Asumsikan beda

        if last_history:
            is_different = (
                last_history.history_name != current_data['history_name'] or
                last_history.history_start_date != current_data['history_start_date'] or
                last_history.history_end_date != current_data['history_end_date'] or
                (last_history.history_structure_type_id.id or False) != current_data['history_structure_type_id'] or
                (last_history.history_department_id.id or False) != current_data['history_department_id'] or
                (last_history.history_job_id.id or False) != current_data['history_job_id']
            )

        # Insert hanya jika data berbeda
        if is_different:
            self.env['contract.history.employee'].create({
                'contract_id': self.id,
                **current_data
            })
            
    def action_export_history(self):
        self.ensure_one()
        return {
            'name': 'Export History Berdasarkan Periode',
            'type': 'ir.actions.act_window',
            'res_model': 'export.history.period.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_contract_id': self.id
            }
        }
