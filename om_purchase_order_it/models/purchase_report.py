from odoo import models, fields, api

class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    under_received = fields.Boolean(
        string='Under Received',
        compute='_compute_under_received',
        store=False,
        search='_search_under_received',
    )

    def _compute_under_received(self):
        for record in self:
            # Tampilkan (True) jika qty_ordered == qty_received dan qty_received != qty_billed
            record.under_received = (
                record.qty_received != record.qty_billed
            )

    @api.model
    def _search_under_received(self, operator, value):
        # operator expected '=', '!='
        # value expected boolean True/False

        # Ambil semua record dulu (atau batasi dengan domain lain)
        all_ids = self.search([]).ids
        records = self.browse(all_ids)

        # Filter manual berdasarkan kondisi qty_received < qty_billed
        filtered_records = records.filtered(lambda r: (r.qty_received != r.qty_billed) == value)

        if operator == '=':
            return [('id', 'in', filtered_records.ids)]
        elif operator == '!=':
            # kebalikan: semua record kecuali filtered_records
            excluded_ids = set(all_ids) - set(filtered_records.ids)
            return [('id', 'in', list(excluded_ids))]
        else:
            return []
