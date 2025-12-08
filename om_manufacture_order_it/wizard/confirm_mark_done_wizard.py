from odoo import fields, models, api


class ConfirmMarkDoneWizard(models.TransientModel):
    _name = 'mrp.confirm.mark.done.wizard'
    _description = 'Konfirmasi Produksi Selesai'

