from odoo import api, models


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    @api.model
    def _calc_new_qty(self, request_line, po_line=None, new_pr_line=False):
        purchase_uom = po_line.product_uom or request_line.product_id.uom_po_id

        rl_qty = 0.0
        # Recompute quantity by adding existing running procurements.
        if new_pr_line:
            rl_qty = po_line.product_uom_qty
        else:
            for prl in po_line.purchase_request_lines:
                for alloc in prl.purchase_request_allocation_ids:
                    rl_qty += alloc.product_uom_id._compute_quantity(
                        alloc.requested_product_uom_qty, purchase_uom
                    )
        qty = rl_qty  # Remove enforcement of supplier min_qty
        return qty
