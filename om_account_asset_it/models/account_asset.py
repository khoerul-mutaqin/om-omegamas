from odoo import models, fields, api

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    total_posted_depreciation_value = fields.Monetary(
        string="Total Depreciation Value",
        compute="_compute_total_posted_depreciation_value",
        currency_field='currency_id'
    )

    @api.depends('depreciation_move_ids.amount_total', 'depreciation_move_ids.state')
    def _compute_total_posted_depreciation_value(self):
        for asset in self:
            posted_moves = asset.depreciation_move_ids.filtered(
                lambda m: m.state == 'posted'
            )
            asset.total_posted_depreciation_value = sum(posted_moves.mapped('amount_total'))
