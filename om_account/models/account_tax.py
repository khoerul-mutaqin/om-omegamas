# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import UserError
from collections import defaultdict
from odoo.tools.float_utils import float_repr, float_round, float_compare

class AccountTax(models.Model):
    _inherit = 'account.tax'

    is_tax_dpp_other = fields.Boolean('Is Tax DPP Other', default=False)
    amount_dpp_other = fields.Float('Amount DPP Other', digits=(16, 16), default=0.0, tracking=True)

    # amount_type = fields.Selection(
    #     default='percent',
    #     string="Tax Computation",
    #     required=True,
    #     tracking=True,
    #     selection=[
    #         ('group', 'Group of Taxes'),
    #         ('fixed', 'Fixed'),
    #         ('percent', 'Percentage'),
    #         ('division', 'Percentage Tax Included'),
    #         ('multiply', 'Multiply by Amount')  # Tipe baru
    #     ],
    #     help="""
    #     - Group of Taxes: The tax is a set of sub taxes.
    #     - Fixed: The tax amount stays the same whatever the price.
    #     - Percentage: The tax amount is a % of the price:
    #         e.g 100 * (1 + 10%) = 110 (not price included)
    #         e.g 110 / (1 + 10%) = 100 (price included)
    #     - Percentage Tax Included: The tax amount is a division of the price:
    #         e.g 180 / (1 - 10%) = 200 (not price included)
    #         e.g 200 * (1 - 10%) = 180 (price included)
    #     - Multiply by Amount: The tax amount is computed by multiplying the base amount:
    #         e.g 100 * 10 = 1000
    #     """
    # )

    # def _eval_tax_amount_price_excluded(self, batch, raw_base, evaluation_context):
    #     """ Eval the tax amount for a single tax during the second ascending order for price-excluded taxes.

    #     [!] Mirror of the same method in account_tax.js.
    #     PLZ KEEP BOTH METHODS CONSISTENT WITH EACH OTHERS.

    #     :param batch:               The batch of taxes containing this tax.
    #     :param raw_base:            The base on which the tax should be computed.
    #     :param evaluation_context:  The context containing all relevant info to compute the tax.
    #     :return:                    The tax amount.
    #     """
    #     self.ensure_one()
    #     if self.amount_type == 'percent':
    #         return raw_base * self.amount / 100.0

    #     if self.amount_type == 'division':
    #         total_percentage = sum(tax.amount for tax in batch) / 100.0
    #         incl_base_multiplicator = 1.0 if total_percentage == 1.0 else 1 - total_percentage
    #         return raw_base * self.amount / 100.0 / incl_base_multiplicator
        
    #     #    999999999
    #     # if self.amount_type == 'multiply':
    #     #     return raw_base * self.amount
    #     #    999999999

    # def _eval_tax_amount_price_included(self, batch, raw_base, evaluation_context):
    #     """ Eval the tax amount for a single tax during the descending order for price-included taxes.

    #     [!] Mirror of the same method in account_tax.js.
    #     PLZ KEEP BOTH METHODS CONSISTENT WITH EACH OTHERS.

    #     :param batch:               The batch of taxes containing this tax.
    #     :param raw_base:            The base on which the tax should be computed.
    #     :param evaluation_context:  The context containing all relevant info to compute the tax.
    #     :return:                    The tax amount.
    #     """
    #     self.ensure_one()
    #     if self.amount_type == 'percent':
    #         total_percentage = sum(tax.amount for tax in batch) / 100.0
    #         to_price_excluded_factor = 1 / (1 + total_percentage) if total_percentage != -1 else 0.0
    #         return raw_base * to_price_excluded_factor * self.amount / 100.0

    #     if self.amount_type == 'division':
    #         return raw_base * self.amount / 100.0
       
    # #    999999999
    #     # if self.amount_type == 'multiply':
    #     #     return raw_base * self.amount
    # #    999999999

    @api.model
    def _get_tax_totals_summary(self, base_lines, currency, company, cash_rounding=None):
        res = super()._get_tax_totals_summary(base_lines, currency, company, cash_rounding)

        # 999999999
        if len(base_lines) > 0 and base_lines[0]['record']._name == 'account.move.line':
            res['total_dpp_other_amount'] = base_lines[0]['record'].move_id.dpp_other_amount
        # 999999999

        return res