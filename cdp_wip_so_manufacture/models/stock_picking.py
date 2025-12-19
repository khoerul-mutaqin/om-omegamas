from odoo import models, api, fields, _
from decimal import Decimal, ROUND_HALF_UP, getcontext
import logging

_logger = logging.getLogger(__name__)

getcontext().prec = 12

class Picking(models.Model):
    _inherit = 'stock.picking'
    
    cdp_is_done = fields.Boolean("done For MO FG", default=False, help="Indicates if this picking is done put to mo")
    
    def _get_sale_from_production(self, picking):
        """Ambil sale.order dari production_ids di picking"""
        so = False
        if picking.production_ids:
            mo = picking.production_ids[0]
            so = (
                mo.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id
                or mo.sale_line_id.order_id
                or mo.procurement_group_id.sale_id
            )
        return so

    def _create_wip_product_for_so(self, so):
        """Create and link a WIP product on SO if not exist"""
        if not so:
            return False
        # jika sudah ada, return it
        if so.cdp_product_wip_id:
            return so.cdp_product_wip_id
        
        categ_wip = self.env['product.category'].search([('cdp_for_product_wip', '=', True)], limit=1)
        # create product
        product = self.env['product.product'].create({
            'name': f'WIP - {so.name}',
            'type': 'consu',
            'sale_ok': False,
            'purchase_ok': False,
            'can_be_expensed': False,
            'is_storable': True,
            'tracking': 'lot',
            'categ_id': categ_wip.id if categ_wip else False,
        })
        try:
            so.write({'cdp_product_wip_id': product.id})
        except Exception:
            # jika field tidak ada atau write gagal, tetap return product
            _logger.warning("Cannot write cdp_product_wip_id to sale.order %s", so.name)
        return product
    
    
    def _create_lot_for_wip(self, product, picking):
        seq = self.env['ir.sequence'].next_by_code('cdp.wip.lot.product') or False
        name = seq or f"WIPLOT/{picking.name}"
        lot = self.env['stock.lot'].create({
            'name': name,
            'product_id': product.id,
            'company_id': picking.company_id.id,
        })
        return lot

    
    
    def _confirm_and_finish_shadow_mo(self, mo, wip_lot):
        # confirm mo , terus assign wip_lot ke lot_producing_id , terus set done mo shadow
        if not mo or not wip_lot:
            return False
        mo.action_confirm()
        
        mo.lot_producing_id = wip_lot.id
        mo.action_assign()
        mo.button_mark_done()
        return True
    
    def _update_parent_mos_progress(self, so, wip_product, shadow_mo, parent_mos=None):
        """
        Distribute WIP lot allocations across parent MOs of SO.
        For each shadow lot (qty=1), distribute equally among remaining parent MOs.
        Each MO gets a stock.move + stock.move.line that mirrors Odoo behavior.
        """
        if not so or not wip_product or not shadow_mo:
            return False

        parent_mos = so.mrp_production_ids
        active_parents = parent_mos.filtered(
            lambda m: not m.cdp_is_shadow_mo and m.state not in ("done", "cancel")
        )
        if not active_parents:
            return False
        
        remaining_count = len(active_parents)
        base_alloc = (Decimal(1) / Decimal(remaining_count)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        allocations = []
        total_alloc = Decimal(0)
        for i, mo in enumerate(active_parents, start=1):
            if i < remaining_count:
                allocations.append(base_alloc)
                total_alloc += base_alloc
            else:
                allocations.append((Decimal(1) - total_alloc).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
        
        production_location = self.env['stock.location'].search([('usage', '=', 'production')], limit=1)

        for parent_mo, alloc in zip(active_parents, allocations):
            _logger.info("Assigning lot %s (alloc=%.6f) to parent MO %s", 
                        shadow_mo.lot_producing_id.name, alloc, parent_mo.name)

            # cari raw move untuk wip_product di parent MO
            raw_move = parent_mo.move_raw_ids.filtered(lambda mv: mv.product_id == wip_product)
            if not raw_move:
                raw_move = self.env["stock.move"].create({
                    "name": f"WIP Consumption for {parent_mo.name}",
                    "product_id": wip_product.id,
                    "product_uom_qty": 0.0,  # diupdate di bawah
                    "product_uom": wip_product.uom_id.id,
                    "location_id": parent_mo.location_src_id.id,
                    # "location_dest_id": parent_mo.location_dest_id.id,
                    "location_dest_id": production_location.id,
                    "raw_material_production_id": parent_mo.id,
                })

            # pastikan ada move line untuk lot ini
            ml = raw_move.move_line_ids.filtered(lambda l: l.lot_id == shadow_mo.lot_producing_id)
            if ml:
                ml.qty_done = alloc
            else:
                self.env["stock.move.line"].create({
                    "move_id": raw_move.id,
                    "product_id": wip_product.id,
                    "product_uom_id": wip_product.uom_id.id,
                    "lot_id": shadow_mo.lot_producing_id.id,
                    "location_id": parent_mo.location_src_id.id,
                    # "location_dest_id": parent_mo.location_dest_id.id,
                    "location_dest_id": production_location.id,
                    "qty_done": alloc,
                })

            raw_move.product_uom_qty = sum(raw_move.move_line_ids.mapped("qty_done"))

        return True
    
    def cdp_create_mo_wip_and_input_finish_product_mo(self, parent_mos):
        for picking in self:
            so = self._get_sale_from_production(picking)
            if not so:
                continue
            # create or get WIP product for SO
            wip_product = self._create_wip_product_for_so(so)
            if not wip_product:
                continue
            
            # create lot for this picking
            wip_lot = self._create_lot_for_wip(wip_product, picking)

            # create shadow MO for this lot and if transfer done
            try:
                if picking.state != 'done':
                    continue
                else:
                    shadow_mo = self._create_shadow_mo(wip_product, wip_lot, picking, so)
            except Exception as e:
                _logger.error("Error creating shadow MO for picking %s: %s", picking.name, str(e))
                continue
            # add mrp_production_ids in so for shadow_mo
            if shadow_mo and so:
                shadow_mo.sale_line_id = so.order_line[0].id
                
            # finalize shadow MO: confirm -> set done -> produce WIP lot
            try:
                self._confirm_and_finish_shadow_mo(shadow_mo, wip_lot)
            except Exception as e:
                _logger.exception("Failed to complete shadow MO %s: %s", shadow_mo.id, e)
                continue
            # update parent MO progress based on completed shadow MO count
            try:
                self._update_parent_mos_progress(so, wip_product, shadow_mo, parent_mos)
            except Exception as e:
                _logger.exception("Failed to update parent MO progress for SO %s: %s", so.name, e)
                
                
    def action_make_mo_wip(self):
        for picking in self:
            # picking.button_validate()
            
            so = self._get_sale_from_production(picking)
            if not so:
                continue
            
            mo_with_qty_gt_one = so.mrp_production_ids.filtered(lambda m: m.product_qty > 1 and not m.cdp_is_shadow_mo)
            if mo_with_qty_gt_one:
                raise UserError("Please Split MO First!!!")
            
            wip_product = self._create_wip_product_for_so(so)
            if not wip_product:
                continue
            
            wip_lot = self._create_lot_for_wip(wip_product, picking)
            try:
                if picking.state != 'done':
                    continue
                else:
                    shadow_mo = self._create_shadow_mo(wip_product, wip_lot, picking, so)
            except Exception as e:
                _logger.error("Error creating shadow MO for picking %s: %s", picking.name, str(e))
                continue
            
            if shadow_mo and so:
                shadow_mo.sale_line_id = so.order_line[0].id
                
            try:
                self._confirm_and_finish_shadow_mo(shadow_mo, wip_lot)
            except Exception as e:
                _logger.exception("Failed to complete shadow MO %s: %s", shadow_mo.id, e)
                continue
            
            # update parent MO progress based on completed shadow MO count
            try:
                self._update_parent_mos_progress(so, wip_product, shadow_mo, parent_mos=None)
            except Exception as e:
                _logger.exception("Failed to update parent MO progress for SO %s: %s", so.name, e)
                
            picking.cdp_is_done = True
        
        
        
    # def action_make_mo_wip(self):
    #     print("makse____")

    # def button_validate(self):
    #     res = super(Picking, self).button_validate()
    #     for picking in self:
    #         so = self._get_sale_from_production(picking)
    #         if not so:
    #             continue
            
    #         # create or get WIP product for SO
    #         wip_product = self._create_wip_product_for_so(so)
    #         if not wip_product:
    #             continue
            
    #         # create lot for this picking
    #         wip_lot = self._create_lot_for_wip(wip_product, picking)

    #         # create shadow MO for this lot and if transfer done
    #         try:
    #             if picking.state != 'done':
    #                 continue
    #             else:
    #                 shadow_mo = self._create_shadow_mo(wip_product, wip_lot, picking, so)
    #         except Exception as e:
    #             _logger.error("Error creating shadow MO for picking %s: %s", picking.name, str(e))
    #             continue
            
    #         # add mrp_production_ids in so for shadow_mo
    #         if shadow_mo and so:
    #             shadow_mo.sale_line_id = so.order_line[0].id
                
    #         # finalize shadow MO: confirm -> set done -> produce WIP lot
    #         try:
    #             self._confirm_and_finish_shadow_mo(shadow_mo, wip_lot)
    #         except Exception as e:
    #             _logger.exception("Failed to complete shadow MO %s: %s", shadow_mo.id, e)
    #             continue
            
    #         # update parent MO progress based on completed shadow MO count
    #         try:
    #             self._update_parent_mos_progress(so, wip_product, shadow_mo)
    #         except Exception as e:
    #             _logger.exception("Failed to update parent MO progress for SO %s: %s", so.name, e)
                
    #     return res
            