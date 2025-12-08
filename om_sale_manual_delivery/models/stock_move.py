# Copyright 2017 Denis Leemann, Camptocamp SA
# Copyright 2021 Iván Todorovich, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, Command
from odoo.tools.misc import clean_context, OrderedSet, groupby
from collections import defaultdict
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class StockMove(models.Model):
    _inherit = "stock.move"


    merge_picking = fields.Selection([
        ('no', 'No'),
        ('yes', 'Yes')
    ], string='Merge Picking', default='no')
    sale_id = fields.Many2one('sale.order', string='Sale Order', related='sale_line_id.order_id')

    def _get_new_picking_values(self):
        # Overload to set carrier_id from the manual delivery wizard
        # Note: sale_manual_delivery is expected to be a manual.delivery record
        res = super()._get_new_picking_values()
        manual_delivery = self.env.context.get("om_sale_manual_delivery")
        if manual_delivery:
            if manual_delivery.partner_id:
                res["partner_id"] = manual_delivery.partner_id.id
            if manual_delivery.carrier_id:
                res["carrier_id"] = manual_delivery.carrier_id.id
        return res

    def _search_picking_for_assignation(self):
        # Overload to filter carrier_id
        # Note: sale_manual_delivery is expected to be a manual.delivery record
        manual_delivery = self.env.context.get("om_sale_manual_delivery")
        if manual_delivery:
            # original domain used in super()
            domain = self._search_picking_for_assignation_domain()
            # Filter on carrier
            if manual_delivery.carrier_id:
                domain += [
                    ("carrier_id", "=", manual_delivery.carrier_id.id),
                ]
            return self.env["stock.picking"].search(domain, limit=1)
        else:
            return super()._search_picking_for_assignation()

    def _key_assign_picking(self):
        self.ensure_one()
        keys = (self.group_id, self.location_id, self.location_dest_id, self.picking_type_id)
        
        # 999999999
        if self.sale_line_id and self.sale_line_id.merge_picking == 'yes': 
            keys = (self.location_id, self.location_dest_id, self.picking_type_id)
        # 999999999
        
        if self.partner_id and not self.group_id:
            keys += (self.partner_id, )
        return keys
    
    def _get_new_picking_values(self):
        """ return create values for new picking that will be linked with group
        of moves in self.
        """
        origins = self.filtered(lambda m: m.origin).mapped('origin')
        origins = list(dict.fromkeys(origins)) # create a list of unique items
        # Will display source document if any, when multiple different origins
        # are found display a maximum of 5
        if len(origins) == 0:
            origin = False
        else:
            origin = ','.join(origins[:5])
            if len(origins) > 5:
                origin += "..."
        partners = self.mapped('partner_id')
        partner = len(partners) == 1 and partners.id or False
        # vals = {
        #     'origin': origin,
        #     'company_id': self.mapped('company_id').id,
        #     'user_id': False,
        #     'group_id': self.mapped('group_id').id,
        #     'partner_id': partner,
        #     'picking_type_id': self.mapped('picking_type_id').id,
        #     'location_id': self.mapped('location_id').id,
        # }

        # 999999999
        vals = {}
        if self.mapped('sale_line_id') and self.mapped('sale_line_id')[0].merge_picking == 'yes': 
            vals = {
            'origin': origin,
            'company_id': self.mapped('company_id').id,
            'user_id': False,
            # 'group_id': self.mapped('group_id').id,
            'partner_id': partner,
            'picking_type_id': self.mapped('picking_type_id').id,
            'location_id': self.mapped('location_id').id,
            }
        else:
            vals = {
            'origin': origin,
            'company_id': self.mapped('company_id').id,
            'user_id': False,
            'group_id': self.mapped('group_id').id,
            'partner_id': partner,
            'picking_type_id': self.mapped('picking_type_id').id,
            'location_id': self.mapped('location_id').id,
            }
        # 999999999

        if self.location_dest_id.ids:
            vals['location_dest_id'] = self.location_dest_id.id
        return vals
    
    def _action_confirm(self, merge=True, merge_into=False):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        :param: merge: According to this boolean, a newly confirmed move will be merged
        in another move of the same picking sharing its characteristics.
        """
        # Use OrderedSet of id (instead of recordset + |= ) for performance
        move_create_proc, move_to_confirm, move_waiting = OrderedSet(), OrderedSet(), OrderedSet()
        to_assign = defaultdict(OrderedSet)
        for move in self:
            if move.state != 'draft':
                continue
            # if the move is preceded, then it's waiting (if preceding move is done, then action_assign has been called already and its state is already available)
            if move.move_orig_ids:
                move_waiting.add(move.id)
            elif move.procure_method == 'make_to_order':
                move_waiting.add(move.id)
                move_create_proc.add(move.id)
            elif move.rule_id and move.rule_id.procure_method == 'mts_else_mto':
                move_create_proc.add(move.id)
                move_to_confirm.add(move.id)
            else:
                move_to_confirm.add(move.id)
            if move._should_be_assigned():
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)

                # 999999999
                if move.sale_line_id and move.sale_line_id.merge_picking == 'yes':
                    key = (move.location_id.id, move.location_dest_id.id)
                # 999999999
                
                to_assign[key].add(move.id)

        # create procurements for make to order moves
        procurement_requests = []
        move_create_proc = self.browse(move_create_proc)
        quantities = move_create_proc._prepare_procurement_qty()
        for move, quantity in zip(move_create_proc, quantities):
            values = move._prepare_procurement_values()
            origin = move._prepare_procurement_origin()
            procurement_requests.append(self.env['procurement.group'].Procurement(
                move.product_id, quantity, move.product_uom,
                move.location_id, move.rule_id and move.rule_id.name or "/",
                origin, move.company_id, values))
        self.env['procurement.group'].run(procurement_requests, raise_user_error=not self.env.context.get('from_orderpoint'))

        move_to_confirm, move_waiting = self.browse(move_to_confirm), self.browse(move_waiting)
        move_to_confirm.write({'state': 'confirmed'})
        move_waiting.write({'state': 'waiting'})
        # procure_method sometimes changes with certain workflows so just in case, apply to all moves
        (move_to_confirm | move_waiting).filtered(lambda m: m.picking_type_id.reservation_method == 'at_confirm')\
            .write({'reservation_date': fields.Date.today()})

        # assign picking in batch for all confirmed move that share the same details
        for moves_ids in to_assign.values():
            self.browse(moves_ids).with_context(clean_context(self.env.context))._assign_picking()

        self._check_company()
        moves = self
        if merge:
            moves = self._merge_moves(merge_into=merge_into)

        neg_r_moves = moves.filtered(lambda move: float_compare(
            move.product_uom_qty, 0, precision_rounding=move.product_uom.rounding) < 0)

        # Push remaining quantities to next step
        neg_to_push = neg_r_moves.filtered(lambda move: move.location_final_id and move.location_dest_id != move.location_final_id)
        new_push_moves = self.env['stock.move']
        if neg_to_push:
            new_push_moves = neg_to_push._push_apply()

        # Transform remaining move in returns in case of negative initial demand
        for move in neg_r_moves:
            move.location_id, move.location_dest_id, move.location_final_id = move.location_dest_id, move.location_id, move.location_id
            orig_move_ids, dest_move_ids = [], []
            for m in move.move_orig_ids | move.move_dest_ids:
                from_loc, to_loc = m.location_id, m.location_dest_id
                if float_compare(m.product_uom_qty, 0, precision_rounding=m.product_uom.rounding) < 0:
                    from_loc, to_loc = to_loc, from_loc
                if to_loc == move.location_id:
                    orig_move_ids += m.ids
                elif move.location_dest_id == from_loc:
                    dest_move_ids += m.ids
            move.move_orig_ids, move.move_dest_ids = [Command.set(orig_move_ids)], [Command.set(dest_move_ids)]
            move.product_uom_qty *= -1
            if move.picking_type_id.return_picking_type_id:
                move.picking_type_id = move.picking_type_id.return_picking_type_id
            # We are returning some products, we must take them in the source location
            move.procure_method = 'make_to_stock'
        neg_r_moves._assign_picking()

        # call `_action_assign` on every confirmed move which location_id bypasses the reservation + those expected to be auto-assigned
        moves.filtered(lambda move: move.state in ('confirmed', 'partially_available')
                       and (move._should_bypass_reservation()
                            or move.picking_type_id.reservation_method == 'at_confirm'
                            or (move.reservation_date and move.reservation_date <= fields.Date.today())))\
             ._action_assign()

        if new_push_moves:
            neg_push_moves = new_push_moves.filtered(lambda sm: float_compare(sm.product_uom_qty, 0, precision_rounding=sm.product_uom.rounding) < 0)
            (new_push_moves - neg_push_moves).sudo()._action_confirm()
            # Negative moves do not have any picking, so we should try to merge it with their siblings
            neg_push_moves._action_confirm(merge_into=neg_push_moves.move_orig_ids.move_dest_ids)
        return moves
    
    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description):
        self.ensure_one()

        # Panggil fungsi original
        rslt = super()._generate_valuation_lines_data(
            partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description
        )

        # Tentukan analytic_distribution jika kondisi terpenuhi
        analytic_distribution = {}
        
        if self.picking_id and self.picking_id.analytic_account_id:
            analytic_distribution = {str(self.picking_id.analytic_account_id.id): 100}

        # Update analytic_distribution hanya jika belum ada
        if analytic_distribution:
            if not rslt['credit_line_vals'].get('analytic_distribution'):
                rslt['credit_line_vals']['analytic_distribution'] = analytic_distribution
            if not rslt['debit_line_vals'].get('analytic_distribution'):
                rslt['debit_line_vals']['analytic_distribution'] = analytic_distribution

        return rslt