# -*- coding: utf-8 -*-
from odoo.tools.sql import create_index, SQL
from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # is_allocated_reconcile = fields.Boolean('Allocated Reconcile', copy=False)
    # number_of_batch = fields.Integer('Number Batch Reconcile', default=0, copay=False)
    dpp_other_amount = fields.Monetary(
        string='DPP Other Amount',
        compute='_compute_dpp_other_amount', store=True,
        currency_field='currency_id',
    )

    cumulated_balance_2 = fields.Monetary(
        string='Cumulated Balance #2',
        compute='_compute_cumulated_balance_2',
        currency_field='currency_id',
        exportable=False,
        help="Cumulated balance #2 depending on the domain and the order chosen in the view.")

    @api.depends('tax_ids', 'price_subtotal', 'tax_ids.amount_type')
    def _compute_dpp_other_amount(self):
        for rec in self:
            # if rec.tax_ids.filtered(lambda x: x.amount_type == 'multiply'):
                # rec.dpp_other_amount = rec.price_subtotal * (rec.tax_ids.filtered(lambda x: x.amount_type == 'multiply').amount)
            if rec.tax_ids.filtered(lambda x: x.is_tax_dpp_other):
                rec.dpp_other_amount = rec.price_subtotal * (rec.tax_ids.filtered(lambda x: x.is_tax_dpp_other).amount_dpp_other)
            else:
                rec.dpp_other_amount = 0
            
    
    # @api.depends_context('order_cumulated_balance', 'domain_cumulated_balance')
    # def _compute_cumulated_balance_2(self):
    #     if not self.env.context.get('order_cumulated_balance'):
    #         # We do not come from search_fetch, so we are not in a list view, so it doesn't make any sense to compute the cumulated balance
    #         self.cumulated_balance_2 = 0
    #         return

    #     # get the where clause
    #     query = self._where_calc(list(self.env.context.get('domain_cumulated_balance') or []))
    #     sql_order = self._order_to_sql(self.env.context.get('order_cumulated_balance'), query, reverse=True)
    #     order_string = self.env.cr.mogrify(sql_order).decode()
    #     from_clause, where_clause, where_clause_params = query.get_sql()
    #     sql = """
    #         SELECT account_move_line.id, SUM(account_move_line.amount_currency) OVER (
    #             ORDER BY %(order_by)s
    #             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    #         )
    #         FROM %(from)s
    #         WHERE %(where)s
    #     """ % {'from': from_clause, 'where': where_clause or 'TRUE', 'order_by': order_string}
    #     self.env.cr.execute(sql, where_clause_params)
    #     result = {r[0]: r[1] for r in self.env.cr.fetchall()}
    #     for record in self:
    #         # record.cumulated_balance_2 = result[record.id] / record._get_currency_rate()
    #         record.cumulated_balance_2 = result[record.id] 

    @api.depends_context('order_cumulated_balance', 'domain_cumulated_balance')
    def _compute_cumulated_balance_2(self):
        if not self.env.context.get('order_cumulated_balance'):
            # We do not come from search_fetch, so we are not in a list view, so it doesn't make any sense to compute the cumulated balance
            self.cumulated_balance_2 = 0
            return

        # Get the where clause
        query = self._where_calc(list(self.env.context.get('domain_cumulated_balance') or []))
        sql_order = self._order_to_sql(self.env.context.get('order_cumulated_balance'), query, reverse=True)
        
        # Use `execute_query` to execute the SQL
        result = dict(self.env.execute_query(query.select(
            SQL.identifier(query.table, "id"),
            SQL(
                "SUM(%s) OVER (ORDER BY %s ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)",
                SQL.identifier(query.table, "amount_currency"),  # Replace balance with amount_currency
                sql_order,
            ),
        )))
        
        # Assign the computed values
        for record in self:
            record.cumulated_balance_2 = result.get(record.id, 0)

       
    def _get_currency_rate(self):     
        for rec in self:
            currency = rec.currency_id
            company_currency = rec.company_currency_id
            # currency = rec.company_currency_id
            # rec.amount_residual_convert = currency._convert(rec.amount_residual_currency, company_currency)
            current_rate =  self.env['res.currency']._get_conversion_rate(
                    from_currency=currency,
                    to_currency=company_currency,
                    company=rec.company_id,
                    date=rec._get_rate_date(),
                )
            return current_rate
