from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class stock_summary(models.Model):
    _name = "fal.stock.summary"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Summary Card"

    name = fields.Char("Number", default="/")
    date_start = fields.Datetime(
        "Date Start", required=True, tracking=True, default=fields.Datetime.today()
    )
    date_end = fields.Datetime(
        "Date End", required=True, tracking=True, default=fields.Datetime.today()
    )
    location_id = fields.Many2one(
        "stock.location", "Location", required=True, tracking=True
    )
    fal_option = fields.Selection(
        [("qty", "Start Qty <> 0"), ("instock", "In Stock"), ("periode", "Period"),('all', 'All Products')],
        "Option",
        default="periode",
    )
    line_ids = fields.One2many("fal.stock.summary.line", "stock_summary_id", "Details")
    breakdown_sn = fields.Boolean("Breakdown Serial Number?")
    state = fields.Selection(
        [("draft", "Draft"), ("open", "Open"), ("done", "Done"), ("post", "Post")],
        "Status",
        readonly=True,
        required=True,
        default="draft",
    )
    user_id = fields.Many2one(
        "res.users", "Created", default=lambda self: self.env.user
    )
    move_id = fields.Many2one("account.move", string="Journal Entries")
    journal_id = fields.Many2one("account.journal", string="Journal")
    stock_valuation_acc = fields.Many2one(
        "account.account", string="Stock Valuation Account"
    )
    expense_acc = fields.Many2one("account.account", string="Expense Account")

    def unlink(self):
        for order in self:
            if order.state not in ("draft"):
                raise UserError(
                    _("In order to delete a stock summary, you must cancel it first.")
                )
        return super(stock_summary, self).unlink()

    def post_journal(self):
        created_moves = self.env["account.move"]
        line_list = []
        for line in self.line_ids:
            name = line.stock_summary_id.name + " - " + line.product_id.name
            product = line.product_id
            qty_in_val = line.qty_in * line.product_id.standard_price
            qty_out_val = line.qty_out * line.product_id.standard_price
            if qty_out_val != qty_in_val:
                diff_val = qty_in_val - qty_out_val
            else:
                diff_val = 0.0

            # Credit
            if qty_out_val > 0.0:
                credit_1 = 0.0
                debit_1 = abs(qty_out_val)
            else:
                credit_1 = abs(qty_out_val)
                debit_1 = 0.0
            move_line_1 = {
                "name": name,
                "account_id": line.stock_summary_id.expense_acc.id,
                "credit": credit_1,
                "debit": debit_1,
                "journal_id": line.stock_summary_id.journal_id.id,
                "product_id": product.id,
                "product_uom_id": line.product_uom_id.id,
            }
            line_list.append((0, 0, move_line_1))
            # Debit
            if qty_in_val > 0.0:
                credit_2 = abs(qty_in_val)
                debit_2 = 0.0
            else:
                credit_2 = 0.0
                debit_2 = abs(qty_in_val)
            move_line_2 = {
                "name": name,
                "account_id": line.stock_summary_id.stock_valuation_acc.id,
                "credit": credit_2,
                "debit": debit_2,
                "journal_id": line.stock_summary_id.journal_id.id,
                "product_id": product.id,
                "product_uom_id": line.product_uom_id.id,
            }
            line_list.append((0, 0, move_line_2))
            if diff_val:
                # Diff Credit and Debit
                if diff_val > 0.0:
                    credit_3 = 0.0
                    debit_3 = abs(diff_val)
                else:
                    credit_3 = abs(diff_val)
                    debit_3 = 0.0
                move_line_3 = {
                    "name": name,
                    "account_id": line.stock_summary_id.stock_valuation_acc.id,
                    "credit": credit_3,
                    "debit": debit_3,
                    "journal_id": line.stock_summary_id.journal_id.id,
                    "product_id": product.id,
                    "product_uom_id": line.product_uom_id.id,
                }
                line_list.append((0, 0, move_line_3))
        move_vals = {
            "ref": line.stock_summary_id.name,
            "date": self.date_end or False,
            "journal_id": line.stock_summary_id.journal_id.id,
            "line_ids": line_list,
        }

        move = created_moves.create(move_vals)
        self.write(
            {
                "move_id": move.id,
                "state": "post",
            }
        )

    def action_calculate(self):
        # kosongkan stock_summary_line
        # cari list produk yang ada stocknya di location id
        # cari stock move product_id dan location_id, start_date to end_date
        # insert into stock_summary_line
        # jika keluar dari location (source_id) maka isi ke qty_out
        # jika masu ke location (dest_id) maka isi ke qty_in
        # hitung qty_balance = qty_start + qty_in - qty_out
        # start balance dihitung dari total qty stock move sebelum start_date

        stock_summary_line = self.env["fal.stock.summary.line"]

        for sc in self:
            self.env.cr.execute(
                "delete from fal_stock_summary_line \
                where stock_summary_id=%s" % sc.id)
                    # add condition for all option
            if sc.fal_option == 'all':
                sc.process_all_product_lines_nosn()
            else:
                self.beginning_lines_nosn(stock_summary_line, sc)
                self.mutasi_lines_nosn(stock_summary_line, sc)
                self.update_balance(sc)
                self.update_other_info(sc)
        return

    def update_other_info(self, sc):
        # set Other Info Data
        line = sc.line_ids
        if line:
            line_vals = line[0]
            categ = line_vals.product_id.categ_id
            if categ:
                journal_id = categ.property_stock_journal.id
                valuation_acc = categ.property_stock_valuation_account_id.id
                expense_acc = categ.property_account_expense_categ_id.id
                return self.write(
                    {
                        "journal_id": journal_id,
                        "stock_valuation_acc": valuation_acc,
                        "expense_acc": expense_acc,
                    }
                )
            else:
                return self.write(
                    {
                        "journal_id": False,
                        "stock_valuation_acc": False,
                        "expense_acc": False,
                    }
                )

    def beginning_lines_nosn(self, stock_summary_line, sc):
        # date = "date < (select date + INTERVAL '1 day' \
        # from stock_move as m where location_dest_id = %s \
        # and date between '%s 00:00:00' \
        # and '%s 00:00:00' and state = 'done' \
        # order by date asc limit 1)" % (
        #     sc.location_id.id, sc.date_start, sc.date_end
        # )
        if sc.fal_option == "qty":
            date = "date < '%s'" % (sc.date_start)
            line_type = "beg"
            self.process_lines_nosn(line_type, date, stock_summary_line, sc)

        else:
            line_type = "beg"
            date = (
                "date >= '%s' and \
                date <= '%s'"
                % (sc.date_start, sc.date_end)
            )
            self.process_lines_nosn(line_type, date, stock_summary_line, sc)

    def mutasi_lines_nosn(self, stock_summary_line, sc):
        date = (
            "date >= '%s' and \
            date <= '%s'"
            % (sc.date_start, sc.date_end)
        )
        line_type = "mut"
        self.process_lines_nosn(line_type, date, stock_summary_line, sc)

    def process_all_product_lines_nosn(self):
        locations = self.env['stock.location'].search([('id', 'child_of', self.location_id.id)]).ids
        tuple_location = '(' + str(locations[0]) + ')' if len(locations) == 1 else tuple(locations)
        instock = self.env['product.product']
        stock_summary_line = self.env['fal.stock.summary.line']
        all_prod = instock.search([('is_storable', '=', True)])

        for prod in all_prod:
            qty_start = 0.0
            qty_out = 0.0
            qty_in = 0.0
            # beginning balance in
            start_date = "date < '%s'" % (self.date_start)
            sql_prod_qty_in = "select sum(quantity_product_uom) from stock_move_line where product_id=%s \
                  and %s and location_dest_id IN %s \
                  and state='done'"
            self.env.cr.execute(sql_prod_qty_in % (
                prod.id, start_date,
                tuple_location))
            res = self.env.cr.fetchone()
            if res and res[0]:
                qty_start = res[0]

            # beginning balance out
            sql_prod_qty_out = "select sum(quantity_product_uom) from stock_move_line where product_id=%s \
                  and %s and location_id IN %s \
                  and state='done'"

            self.env.cr.execute(sql_prod_qty_out  % (prod.id, start_date, tuple_location))
            res_prod_qty_out = self.env.cr.fetchone()

            if res_prod_qty_out and res_prod_qty_out[0]:
                qty_start = qty_start - res_prod_qty_out[0]

            # QTY IN
            date_between = "date >= '%s' and \
                date <= '%s'" % (self.date_start, self.date_end)
            self.env.cr.execute(sql_prod_qty_in % (
                prod.id, date_between,
                tuple_location))
            res_qty_in = self.env.cr.fetchone()
            if res_qty_in and res_qty_in[0]:
                qty_in = res_qty_in[0]

            # QTY OUT
            self.env.cr.execute(sql_prod_qty_out  % (prod.id, date_between, tuple_location))
            res_qty_out = self.env.cr.fetchone()
            if res_qty_out and res_qty_out[0]:
                qty_out = res_qty_out[0]

            product_uom_id = prod.uom_id.id

            stock_summary_line.create({
                "stock_summary_id": self.id,
                "product_id": prod.id,
                "product_uom_id": product_uom_id,
                "qty_start": qty_start,
                "qty_in": qty_in,
                "qty_out": qty_out,
                "qty_balance": qty_start + qty_in - qty_out,
            })

    def process_lines_nosn(self, line_type, date, stock_summary_line, sc):
        locations = (
            self.env["stock.location"]
            .search([("id", "child_of", sc.location_id.id)])
            .ids
        )
        tuple_location = (
            "(" + str(locations[0]) + ")" if len(locations) == 1 else tuple(locations)
        )
        instock = self.env["product.product"]

        # ORIGINAL CODE
        sql = "select product_id,\
            product_uom_id,\
            sum(quantity_product_uom) \
            from stock_move_line as m \
            where %s and %s IN %s \
            and state = 'done' \
            group by product_id,product_uom_id \
            order by product_id"

        # add condition for instock option (#4800)
        if sc.fal_option == "instock" and line_type == "beg":
            all_prod = instock.search([("qty_available", ">", 0)])
            for prod in all_prod:
                product_uom_id = prod.uom_id.id
                stock_summary_line.create(
                    {
                        "stock_summary_id": sc.id,
                        "product_id": prod.id,
                        "product_uom_id": product_uom_id,
                        "qty_start": 0,
                        "qty_in": 0,
                        "qty_out": 0,
                        "qty_balance": 0,
                    }
                )

        if line_type == "beg":
            sql_beg = """
                SELECT
                    product_id,
                    product_uom_id,
                    SUM(quantity_product_uom) AS total_qty
                FROM stock_move_line AS m
                WHERE
                    %s AND
                    (m.location_id IN %s OR m.location_dest_id IN %s)
                    AND m.state = 'done'
                GROUP BY product_id, product_uom_id
                ORDER BY product_id
            """
            self.env.cr.execute(sql_beg % (date, tuple_location, tuple_location))

            res = self.env.cr.fetchall()
            if not res or res[0] == "None":
                pass

            for beg in res:
                qty_start = 0.0
                # calculate qty_start
                sql2 = (
                    "select id from \
                    stock_move_line where product_id = %s"
                    % (beg[0])
                )
                self.env.cr.execute(sql2)
                res = self.env.cr.fetchall()
                move_ids = []
                if res and res[0] != "None":
                    for move in res:
                        move_ids.append(move[0])
                else:
                    raise UserError(_("No Data for this Product!"))

                # beginning balance in
                sql_prod_qty_in = (
                    "select sum(quantity_product_uom) from stock_move_line where product_id=%s \
                      and date < '%s' and location_dest_id IN %s \
                      and id IN %s \
                      and state='done'"
                    % (
                        beg[0],
                        sc.date_start,
                        tuple_location,
                        "(%s)" % ", ".join(map(repr, tuple(move_ids))),
                    )
                )

                self.env.cr.execute(sql_prod_qty_in)
                res = self.env.cr.fetchone()

                if res and res[0]:
                    qty_start = res[0]

                # beginning balance out
                sql_prod_qty_out = (
                    "select sum(quantity) from stock_move_line \
                    where product_id=%s and date < '%s' and \
                    location_id IN %s and state='done'"
                    % (beg[0], sc.date_start, tuple_location)
                )

                self.env.cr.execute(sql_prod_qty_out)
                res_prod_qty_out = self.env.cr.fetchone()

                if res_prod_qty_out and res_prod_qty_out[0]:
                    qty_start = qty_start - res_prod_qty_out[0]

                product_id = beg[0]
                sm_uom_id = beg[1]
                qty = beg[2]
                qty, product_uom_id = self.convert_uom_qty(product_id, sm_uom_id, qty)
                data = {
                    "stock_summary_id": sc.id,
                    "product_id": product_id,
                    "product_uom_id": product_uom_id,
                    "qty_start": qty_start,
                    "qty_in": 0,
                    "qty_out": 0,
                    "qty_balance": 0,
                }
                if sc.fal_option == "qty":
                    if qty_start > 0:
                        stock_summary_line.create(data)
                elif sc.fal_option == "instock":
                    # pre-made inventory list then update quantity(#4800)

                    if instock.browse(beg[0]).qty_available:
                        sql2 = (
                            "update fal_stock_summary_line set \
                        qty_start = %s \
                        where stock_summary_id = %s and \
                        product_id=%s"
                            % (qty_start, sc.id, product_id)
                        )
                        self.env.cr.execute(sql2)
                else:
                    # tiket this contex come from fal_stock_card_inventory_management ,ticket id: 10904
                    # skip create line jika product tidak di pilih di invetory adjument
                    context_product_ids = self._context.get('fal_product_ids')
                    if context_product_ids and product_id not in context_product_ids:
                        continue

                    stock_summary_line.create(data)
        else:
            self.env.cr.execute(sql % (date, "location_dest_id", tuple_location))

            res = self.env.cr.fetchall()
            if not res or res[0] == "None":
                pass
            for incoming in res:
                product_id = incoming[0]
                sm_uom_id = incoming[1]
                qty = incoming[2]
                qty, product_uom_id = self.convert_uom_qty(product_id, sm_uom_id, qty)
                sql2 = (
                    "update fal_stock_summary_line set \
                        qty_in = %s \
                        where stock_summary_id = %s and \
                        product_id=%s"
                    % (qty, sc.id, product_id)
                )
                self.env.cr.execute(sql2)

        # outgoing
        self.env.cr.execute(sql % (date, "location_id", tuple_location))

        res = self.env.cr.fetchall()
        if not res or res[0] == "None":
            pass

        if res:
            for outgoing in res:
                product_id = outgoing[0]
                sm_uom_id = outgoing[1]
                qty3 = abs(outgoing[2])
                qty3, product_uom_id = self.convert_uom_qty(product_id, sm_uom_id, qty3)

                sql2 = """update fal_stock_summary_line set \
                            qty_out = %s \
                            where stock_summary_id = %s and \
                            product_id=%s """ % (
                    qty3,
                    sc.id,
                    product_id,
                )
                self.env.cr.execute(sql2)

        # balance
        sql = """update fal_stock_summary_line \
            set qty_balance = qty_start + qty_in - qty_out \
            where stock_summary_id = %s """ % (
            sc.id
        )
        self.env.cr.execute(sql)

    def convert_uom_qty(self, product_id, sm_uom_id, qty):
        product = self.env["product.product"].browse(product_id)
        uom = self.env["uom.uom"].browse(sm_uom_id)

        if uom.id != product.uom_id.id:
            factor = product.uom_id.factor / uom.factor
        else:
            factor = 1.0

        converted_qty = qty * factor

        return converted_qty, product.uom_id.id

    def update_balance(self, sc):
        sql3 = (
            "update fal_stock_summary_line set \
            qty_balance =  coalesce( qty_start,0) + \
            coalesce(qty_in,0) - coalesce(qty_out,0) \
            where stock_summary_id = %s "
            % (sc.id)
        )
        self.env.cr.execute(sql3)

    def action_draft(self):
        moves = self.env["account.move"]
        for stock in self:
            if stock.move_id:
                moves += stock.move_id
        # First, set the stock summary as cancelled and detach the move ids
        self.write({"state": "draft", "move_id": False})
        if moves:
            # second, invalidate the move(s)
            moves.button_cancel()
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            moves.unlink()
        return True

    def action_confirm(self):
        # set to "confirmed" state
        return self.write({"state": "open"})

    def action_done(self):
        # set to "done" state
        return self.write({"state": "done"})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fal.stock.summary") or "/"
                )
        new_id = super(stock_summary, self).create(vals_list)
        return new_id


class stock_summary_line(models.Model):
    _name = "fal.stock.summary.line"
    _description = "Summary Card Line"

    name = fields.Char("Description")
    stock_summary_id = fields.Many2one("fal.stock.summary", "Stock Card", ondelete='cascade')
    product_id = fields.Many2one("product.product", "Product")
    product_uom_id = fields.Many2one("uom.uom", "UoM")
    lot_id = fields.Many2one("stock.lot", "Serial Number")
    expired_date = fields.Date(string="Expired Date")
    qty_start = fields.Float("Start")
    qty_in = fields.Float("Qty In")
    qty_out = fields.Float("Qty Out")
    qty_balance = fields.Float("Balance")
