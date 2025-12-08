from datetime import datetime

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'

    def make_purchase_order(self):
        res = []
        purchase_obj = self.env["purchase.order"]
        po_line_obj = self.env["purchase.order.line"]
        pr_line_obj = self.env["purchase.request.line"]
        user_tz = pytz.timezone(self.env.user.tz or "UTC")
        purchase = False

        for item in self.item_ids:
            line = item.line_id
            # Validation: Ensure product_qty in RFQ does not exceed remaining quantity in purchase.request.line
            if item.product_qty > item.remaining_qty:
                raise UserError(
                    _("The quantity (%s) for product '%s' in the RFQ cannot exceed the remaining quantity (%s) in the Purchase Request Line.") % (
                        item.product_qty, line.product_id.display_name, item.remaining_qty
                    )
                )
            # Proceed with original logic
            if item.product_qty <= 0.0:
                raise UserError(_("Enter a positive quantity."))
            if self.purchase_order_id:
                purchase = self.purchase_order_id
            if not purchase:
                po_data = self._prepare_purchase_order(
                    line.request_id.picking_type_id,
                    line.request_id.group_id,
                    line.company_id,
                    line.origin,
                )
                
                # ---- override di sini ----
                last_order = purchase_obj.search([('name', 'like', 'Draft-%')], order="name desc", limit=1)
                if last_order and last_order.name and last_order.name.startswith("Draft-"):
                    try:
                        last_number = int(last_order.name.split('-')[-1])
                        new_number = last_number + 1
                    except ValueError:
                        new_number = 1
                else:
                    new_number = 1
                draft_name = f"Draft-{new_number:02d}"
                
                # buang name bawaan '/' lalu set draft_name
                po_data.pop("name", None)
                po_data["name"] = draft_name
                # --------------------------

                purchase = purchase_obj.create(po_data)

            # Look for any other PO line in the selected PO with same
            # product and UoM to sum quantities instead of creating a new
            # po line
            uom_pr_line = item.product_uom_id
            domain = self._get_order_line_search_domain(purchase, item, uom_pr_line)
            available_po_lines = po_line_obj.search(domain)
            new_pr_line = True
            # If Unit of Measure is not set, update from wizard.
            if not line.product_uom_id:
                line.product_uom_id = item.product_uom_id
            # Allocation UoM has to be the same as PR line UoM
            alloc_uom = line.product_uom_id
            wizard_uom = item.product_uom_id
            if available_po_lines and not item.keep_description:
                new_pr_line = False
                po_line = available_po_lines[0]
                po_line.purchase_request_lines = [(4, line.id)]
                po_line.move_dest_ids |= line.move_dest_ids
                po_line_product_uom_qty = po_line.product_uom._compute_quantity(
                    po_line.product_uom_qty, alloc_uom
                )
                wizard_product_uom_qty = wizard_uom._compute_quantity(
                    item.product_qty, alloc_uom
                )
                all_qty = min(po_line_product_uom_qty, wizard_product_uom_qty)
                self.create_allocation(po_line, line, all_qty, alloc_uom)
            else:
                po_line_data = self._prepare_purchase_order_line(purchase, item)
                if item.keep_description:
                    po_line_data["name"] = item.name
                po_line = po_line_obj.create(po_line_data)
                po_line_product_uom_qty = po_line.product_uom._compute_quantity(
                    po_line.product_uom_qty, alloc_uom
                )
                wizard_product_uom_qty = wizard_uom._compute_quantity(
                    item.product_qty, alloc_uom
                )
                all_qty = min(po_line_product_uom_qty, wizard_product_uom_qty)
                self.create_allocation(po_line, line, all_qty, alloc_uom)
            # TODO: Check propagate_uom compatibility:
            new_qty = pr_line_obj._calc_new_qty(
                line, po_line=po_line, new_pr_line=new_pr_line
            )
            po_line.product_qty = new_qty
            # The quantity update triggers a compute method that alters the
            # unit price (which is what we want, to honor graduate pricing)
            # but also the scheduled date which is what we don't want.
            date_required = item.line_id.date_required
            # we enforce to save the datetime value in the current tz of the user
            po_line.date_planned = (
                user_tz.localize(
                    datetime(date_required.year, date_required.month, date_required.day)
                )
                .astimezone(pytz.utc)
                .replace(tzinfo=None)
            )
            res.append(purchase.id)

        return {
            "domain": [("id", "in", res)],
            "name": _("RFQ"),
            "view_mode": "list,form",
            "res_model": "purchase.order",
            "view_id": False,
            "context": False,
            "type": "ir.actions.act_window",
        }

    @api.model
    def _prepare_item(self, line):
        res = super()._prepare_item(line)
        return res


class PurchaseRequestLineMakePurchaseOrderItem(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order.item'

    remaining_qty = fields.Float(
        string="Remaining Quantity",
        digits="Product Unit of Measure",
        compute='_compute_remaining_qty',
        readonly=True,
        help="Remaining quantity available for RFQ from this Purchase Request Line."
    )

    @api.depends('line_id')
    def _compute_remaining_qty(self):
        for item in self:
            if item.line_id:
                # Calculate remaining quantity: original qty minus qty from all linked PO lines (including drafts)
                allocated_qty = sum(item.line_id.purchase_lines.filtered(lambda pl: pl.order_id.state != 'cancel').mapped('product_qty'))
                item.remaining_qty = item.line_id.product_qty - allocated_qty
            else:
                item.remaining_qty = 0.0

