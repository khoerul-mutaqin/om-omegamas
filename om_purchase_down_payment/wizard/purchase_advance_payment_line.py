# Copyright 2019 Elico Corp, Dominique K. <dominique.k@elico-corp.com.sg>
# Copyright 2019 Ecosoft Co., Ltd., Kitti U. <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from datetime import datetime

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.fields import Command
from odoo.tools import format_date, frozendict

class PurchaseAdvancePaymentInvLine(models.TransientModel):
    _name = "purchase.advance.payment.inv.line"
    _description = "Purchase Advance Payment Invoice Line"

    advance_payment_id = fields.Many2one('purchase.advance.payment.inv')
    purchase_id = fields.Many2one('purchase.order', 'Order')
    dp_blanket = fields.Float('Down Payment', related='purchase_id.dp_blanket')
    dp_order = fields.Float(string="Order Down Payment")
    dp_sisa = fields.Float(string="Remaining Down Payment")

    @api.onchange('dp_order')
    def _onchange_dp_order(self):
        for rec in self:
            if rec.advance_payment_id.advance_payment_method == 'percentage':
                rec.dp_sisa = rec.dp_blanket * rec.dp_order
            if rec.advance_payment_id.advance_payment_method == 'fixed':
                rec.dp_sisa = rec.dp_blanket - rec.dp_order


    