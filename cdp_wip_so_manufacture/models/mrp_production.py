# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import datetime
import math
import re

from ast import literal_eval
from collections import defaultdict
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    cdp_is_shadow_mo = fields.Boolean("Is Shadow MO", default=False, help="Indicates if this manufacturing order is a shadow MO created for WIP tracking.")
    cdp_mrp_production_shadow_id = fields.Many2one('mrp.production', "Shadow MO", help="Link to the shadow MO created for WIP tracking.")
    
    # def cdp_search_picking_done(self):
    #     return self.picking_ids.filtered(
    #         lambda p: p.state == "done" and not p.cdp_is_done
    #     )[:1]
        
    def _get_done_picking_from_so(self, so):
        """Ambil 1 picking done (belum diproses) dari semua MO non-shadow di SO."""
        if not so:
            return self.env['stock.picking']
        mos = so.mrp_production_ids.filtered(lambda m: not m.cdp_is_shadow_mo)
        pickings = mos.mapped('picking_ids')
        return pickings.filtered(lambda p: p.state == 'done' and not p.cdp_is_done)[:1]
        
    def _get_sale_from_production(self):
        """Ambil sale.order dari production_ids di picking"""
        return self.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id or self.sale_line_id.order_id or self.procurement_group_id.sale_id
        
    def cdp_create_mo_wip_and_input_finish_product(self):
        for rec in self:
            
            so = rec._get_sale_from_production()
            mo_with_qty_gt_one = so.mrp_production_ids.filtered(lambda m: m.product_qty > 1 and not m.cdp_is_shadow_mo)
            
            if mo_with_qty_gt_one:
                raise UserError("Please Split MO First!!!")
            picking_done = self._get_done_picking_from_so(so)
            if not picking_done:
                continue
            picking_done.sudo().write({
                'cdp_is_done': True
            })
            picking_done.sudo().cdp_create_mo_wip_and_input_finish_product_mo(self)
