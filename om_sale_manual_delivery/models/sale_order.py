# Copyright 2017 Denis Leemann, Camptocamp SA
# Copyright 2021 Iván Todorovich, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    manual_delivery = fields.Boolean(
        default=lambda self: self.env.company.sale_manual_delivery,
        help="If enabled, the deliveries are not created at SO confirmation. "
        "You need to use the Create Delivery button in order to reserve "
        "and ship the goods.",
    )


    has_pending_delivery = fields.Boolean(
        string="Delivery pending?",
        compute="_compute_delivery_pending",
    )

    is_fully_delivered_or_invoiced = fields.Char(compute='_compute_is_fully_delivered_or_invoiced', string='Fully Delivered / Invoiced')

    
    @api.depends('order_line')
    def _compute_is_fully_delivered_or_invoiced(self):
        for rec in self:
            rec.is_fully_delivered_or_invoiced = all([line.product_uom_qty == line.qty_delivered and line.product_qty == line.qty_invoiced for line in rec.order_line.filtered(lambda x: not x.is_downpayment) ])



    def _compute_delivery_pending(self):
        for rec in self:
            lines_pending = rec.order_line.filtered(
                lambda x: x.product_id.type != "service" and x.qty_to_procure > 0
            )
            rec.has_pending_delivery = bool(lines_pending)

    # @api.onchange("team_id")
    # def _onchange_team_id(self):
    #     self.manual_delivery = self.team_id.manual_delivery



    @api.constrains("manual_delivery")
    def _check_manual_delivery(self):
        if any(rec.state not in ["draft", "sent"] for rec in self):
            raise UserError(
                _(
                    "You can only change to/from manual delivery"
                    " in a quote, not a confirmed order"
                )
            )

    @api.depends('picking_ids', 'picking_ids.move_ids')
    def _compute_picking_ids(self):
        for order in self:
            sale_group = self.env['procurement.group'].search([('name', '=', order.name)])
            pickings = sale_group.stock_move_ids.picking_id or order.picking_ids
            for rec in self.order_line:
                sm = self.env['stock.move'].search([('sale_line_id', '=', rec.id)])
                if sm:
                    pickings|= sm.picking_id


            order.delivery_count = len(pickings)

    def _get_action_view_picking(self, pickings):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        sale_group = self.env['procurement.group'].search([('name', '=', self.name)])    
        pickings = sale_group.stock_move_ids.picking_id or pickings
    
        for rec in self.order_line:
            sm = self.env['stock.move'].search([('sale_line_id', '=', rec.id)])
            if sm:
                pickings|= sm.picking_id


        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")

        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        # Prepare the context.
        picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = pickings[0]
        action['context'] = dict(default_partner_id=self.partner_id.id, default_picking_type_id=picking_id.picking_type_id.id, default_origin=self.name, default_group_id=picking_id.group_id.id)
        return action
        
            
    