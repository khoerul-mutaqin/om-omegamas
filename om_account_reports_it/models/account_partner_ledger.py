from odoo import models, api, _
from odoo.tools.misc import formatLang


class AccountPartnerLedger(models.AbstractModel):
    _inherit = 'account.partner.ledger.report.handler'

    @api.model
    def _build_partner_lines(self, report, options):
        """
        Override untuk menambahkan total Amount Currency dalam laporan Partner Ledger.
        """
        partner_lines, totals_by_column_group = super()._build_partner_lines(report, options)

        # Reset nilai amount_currency sebelum dihitung ulang
        for column_group in totals_by_column_group.values():
            column_group['amount_currency'] = 0.0

        # Akumulasi nilai amount_currency dari semua partner
        for partner_line in partner_lines:
            for column_group_key, columns in partner_line.items():
                if column_group_key in totals_by_column_group:
                    totals_by_column_group[column_group_key]['amount_currency'] += columns.get('amount_currency', 0.0)

        return partner_lines, totals_by_column_group

    @api.model
    def _dynamic_lines_generator(self, report, options, all_column_groups_expression_totals, warnings=None):
        """
        Override untuk memastikan total Amount Currency ditampilkan dalam laporan.
        """
        lines = super()._dynamic_lines_generator(report, options, all_column_groups_expression_totals,
                                                 warnings=warnings)

        # Tambahkan Total Line jika belum ada dan perbarui nilainya
        total_line = next((line[1] for line in lines if line[1].get('name') == _('Total')), None)
        if total_line:
            for column_group_key, totals in all_column_groups_expression_totals.items():
                total_line['columns'].insert(0, {'name': self.format_value(totals.get('amount_currency', 0.0))}) # Sesuaikan index jika perlu
        else:
            total_line = self._get_report_line_total(options, all_column_groups_expression_totals)
            if total_line:
                lines.append((0, total_line))
        return lines

    @api.model
    def _custom_options_initializer(self, report, options, previous_options=None):
        """
        Override untuk memastikan Amount Currency tetap ada jika multi-currency aktif.
        """
        super()._custom_options_initializer(report, options, previous_options)

        # Pastikan kolom amount_currency tetap ada jika multi currency aktif
        if self.env.user.has_group('base.group_multi_currency'):
            options['multi_currency'] = True
            # Tambahkan kolom amount_currency jika belum ada
            if not any(col.get('expression_label') == 'amount_currency' for col in options['columns']):
                options['columns'].insert(0, {'name': _('Amount Currency'), 'expression_label': 'amount_currency'}) # Sesuaikan index jika perlu
        else:
            options['columns'] = [
                col for col in options['columns']
                if col.get('expression_label') != 'amount_currency'
            ]
    @api.model
    def format_value(self, value):
        """
        Override untuk format value sesuai dengan pengaturan Odoo
        """
        # return format_value(value, currency=self.env.company.currency_id)

        return formatLang(self.env, value, currency_obj=self.env.company.currency_id)

    @api.model
    def _get_report_line_total(self, options, all_column_groups_expression_totals):
        """
        Override untuk menambahkan amount currency ke total line
        """
        total_line = super()._get_report_line_total(options, all_column_groups_expression_totals)
        if total_line:
            total_line['name'] = _('Total')
            total_line['class'] = 'total'
            columns = []
            for column_group_key in options['column_groups']:
                totals = all_column_groups_expression_totals[column_group_key]
                columns.append({'name': self.format_value(totals.get('amount_currency', 0.0))})
                columns.append({'name': self.format_value(totals.get('debit', 0.0))})
                columns.append({'name': self.format_value(totals.get('credit', 0.0))})
                columns.append({'name': self.format_value(totals.get('balance', 0.0))})

            total_line['columns'] = columns
        return total_line
