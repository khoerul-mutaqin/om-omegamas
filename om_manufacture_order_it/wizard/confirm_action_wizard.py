from odoo import fields, models, api


class ConfirmActionWizard(models.TransientModel):
    _name = 'mrp.confirm.action.wizard'
    _description = 'Konfirmasi Produksi'

