from collections import defaultdict
from odoo import api, models, fields, _
from odoo.tools import float_is_zero, float_repr, float_round, float_compare
from odoo.exceptions import UserError
class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    no_ttb = fields.Text('No. TTB')


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_in_svl_vals(self, forced_quantity):
        svl_vals_list = []
        for move in self:
            move = move.with_company(move.company_id)
            lines = move._get_in_move_lines()
            quantities = defaultdict(float)
            if forced_quantity:
                quantities[forced_quantity[0]] += forced_quantity[1]
            else:
                for line in lines:
                    quantities[line.lot_id] += line.product_uom_id._compute_quantity(
                        line.quantity, move.product_id.uom_id
                    )
            if move.product_id.lot_valuated:
                unit_cost = {lot: lot.standard_price for lot in move.lot_ids}
            else:
                unit_cost = {self.env['stock.lot']: move.product_id.standard_price}
            if move.product_id.cost_method != 'standard':
                unit_cost = move._get_price_unit()  # May be negative (i.e. decrease an out move).
            if self.env.company.last_cost_price:
                unit_cost = move._get_price_unit()
            if move.product_id.lot_valuated:
                vals = []
                for lot_id, qty in quantities.items():
                    vals.append(move.product_id._prepare_in_svl_vals(qty, abs(unit_cost[lot_id]), lot=lot_id))
            else:
                vals = [move.product_id._prepare_in_svl_vals(sum(quantities.values()), abs(unit_cost[self.env['stock.lot']]))]
            for val in vals:
                val.update(move._prepare_common_svl_vals())
                if forced_quantity:
                    val['description'] = _('Correction of %s (modification of past move)', move.picking_id.name or move.name)
            svl_vals_list += vals
        return svl_vals_list

   
    
    # def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description):
    #     self.ensure_one()

    #     # Panggil fungsi original
    #     rslt = super()._generate_valuation_lines_data(
    #         partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description
    #     )

    #     # Tentukan analytic_distribution jika kondisi terpenuhi
    #     analytic_distribution = {}
    #     if self.raw_material_production_id and self.raw_material_production_id.analytic_account_id:
    #     # if self.raw_material_production_id and self.raw_material_production_id.project_id and self.raw_material_production_id.project_id.account_id:
    #         analytic_distribution = {str(self.raw_material_production_id.project_id.account_id.id): 100}

    #     # Update analytic_distribution hanya jika belum ada
    #     if analytic_distribution:
    #         if not rslt['credit_line_vals'].get('analytic_distribution'):
    #             rslt['credit_line_vals']['analytic_distribution'] = analytic_distribution
    #         if not rslt['debit_line_vals'].get('analytic_distribution'):
    #             rslt['debit_line_vals']['analytic_distribution'] = analytic_distribution

    #     return rslt

# class InheritProductProduct(models.Model):
#     _inherit = 'product.product'

    # def _prepare_out_svl_vals(self, quantity, company):
    #     self.ensure_one()
    #     company_id = self.env.context.get('force_company', self.env.company.id)
    #     company = self.env['res.company'].browse(company_id)
    #     currency = company.currency_id
    #     # quantity = -abs(quantity)  # Ensure quantity is negative for out valuation layers
    #     quantity = -1 * quantity
    #     vals = {
    #         'product_id': self.id,
    #         # 'unit_cost': 0.0,  # Default unit cost
    #         'unit_cost': self.standard_price,
    #         'quantity': quantity,
    #     }

    #     po = False
    #     if self.env.context.get('active_model') == 'purchase.order':
    #         po = self.env['purchase.order'].search([('id', '=', self.env.context['active_id'])], limit=1)
    #     if self.env.context.get('active_model') == 'stock.picking':
    #         picking = self.env['stock.picking'].search([('id', '=', self.env.context['active_id'])], limit=1)
    #         if picking.purchase_id:
    #             po = self.env['purchase.order'].search([('id', '=', picking.purchase_id.id)], limit=1)

    #     if po and po.order_line: 
    #         order_line = po.order_line.filtered(lambda line: line.product_id.id == self.id)
    #         if order_line:
    #             vals['unit_cost'] = order_line[0].price_unit
    #             vals['value'] = currency.round(quantity * order_line[0].price_unit)
    #         # for line in po.order_line:
    #         #     if line.product_id.id == self.id:
    #         #         vals['unit_cost'] = line.price_unit


    #     # Ensure we are referencing the correct stock valuation layer for the return
    #     if 'return_reference' in self.env.context:
    #         original_svl = self.env['stock.valuation.layer'].search([
    #             ('reference', '=', self.env.context['return_reference']),
    #             ('product_id', '=', self.id),
    #             ('quantity', '>', 0)  # Incoming stock moves only
    #         ], limit=1)
    #     else:
    #         original_svl = None

    #     if original_svl:
    #         # Identify the picking and the purchase order related to this SVL
    #         pick = self.env['stock.picking'].search([('name', '=', original_svl.reference)], limit=1)
    #         if pick and pick.purchase_id:
    #             purchase_order = pick.purchase_id
    #             # Retrieve the original purchase order line associated with the current product and PO
    #             purchase_line = self.env['purchase.order.line'].search([
    #                 ('product_id', '=', self.id),
    #                 ('order_id', '=', purchase_order.id)
    #             ], limit=1)

    #             if purchase_line:
    #                 # Set unit cost from the PO line for the return's valuation layer
    #                 vals['unit_cost'] = purchase_line.price_unit
    #                 vals['value'] = currency.round(-quantity * purchase_line.price_unit)

    #     # Handle cases where the product cost method is FIFO or average
    #     # if self.product_tmpl_id.cost_method in ['fifo', 'average']:
    #     if self.product_tmpl_id.cost_method in ['fifo']:
    #         fifo_vals = self._run_fifo(abs(quantity), company)
    #         vals.update(fifo_vals)

    #     return vals
