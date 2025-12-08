from odoo import _, api, fields, models


class GeneralLedgerReport(models.AbstractModel):
    _inherit = 'account.general.ledger.report.handler'

    def _get_columns_name(self, options):
        """Override column names to add (IDR) suffix and Balance (Currency) column"""
        columns = super()._get_columns_name(options) if hasattr(super(), '_get_columns_name') else []
        
        # Modify existing column names to add (IDR) suffix
        for column in options.get('columns', []):
            if column.get('expression_label') == 'debit':
                column['name'] = 'Debit (IDR)'
            elif column.get('expression_label') == 'credit':
                column['name'] = 'Credit (IDR)'
            elif column.get('expression_label') == 'balance':
                column['name'] = 'Balance (IDR)'
        
        return columns

    def _custom_options_initializer(self, report, options, previous_options):
        """Initialize custom options and modify column headers"""
        super()._custom_options_initializer(report, options, previous_options)
        
        # Add Balance (Currency) column to options if not exists
        currency_col_index = -1
        balance_currency_exists = False
        
        for i, column in enumerate(options.get('columns', [])):
            if column.get('expression_label') == 'amount_currency':
                currency_col_index = i
            elif column.get('expression_label') == 'balance_currency':
                balance_currency_exists = True
            # Update column names with (IDR) suffix
            elif column.get('expression_label') == 'debit':
                column['name'] = 'Debit (IDR)'
            elif column.get('expression_label') == 'credit':
                column['name'] = 'Credit (IDR)'
            elif column.get('expression_label') == 'balance':
                column['name'] = 'Balance (IDR)'
        
        # Add Balance (Currency) column after Currency column if not exists
        if currency_col_index != -1 and not balance_currency_exists:
            currency_column = options['columns'][currency_col_index]
            balance_currency_column = {
                'name': 'Balance (Currency)',
                'expression_label': 'balance_currency',
                'figure_type': 'monetary',
                'column_group_key': currency_column.get('column_group_key'),
                'sortable': False,
            }
            options['columns'].insert(currency_col_index + 1, balance_currency_column)

    def _dynamic_lines_generator(self, report, options, all_column_groups_expression_totals, warnings=None):
        lines = super()._dynamic_lines_generator(report, options, all_column_groups_expression_totals, warnings)
        
        # Track running balance per account for Balance (Currency)
        balance_currency_running = {}
        
        for line_tuple in lines:
            line = line_tuple[1]  # Get the line dict from tuple
            
            if line.get('columns') and line.get('level') == 1:  # Account level lines
                account_id = line.get('id')
                if not account_id:
                    continue

                # Initialize running balance per account
                if account_id not in balance_currency_running:
                    balance_currency_running[account_id] = 0.0

                # Find amount_currency column value
                amount_currency = 0.0
                currency_col_index = -1
                
                for i, col in enumerate(line['columns']):
                    if col.get('expression_label') == 'amount_currency':
                        amount_currency = col.get('no_format', 0.0) or 0.0
                        currency_col_index = i
                        break

                # Update running balance
                balance_currency_running[account_id] += amount_currency

                # Add or update Balance (Currency) column
                balance_currency_col_index = -1
                for i, col in enumerate(line['columns']):
                    if col.get('expression_label') == 'balance_currency':
                        balance_currency_col_index = i
                        break

                if balance_currency_col_index != -1:
                    # Update existing Balance (Currency) column
                    line['columns'][balance_currency_col_index].update({
                        'name': self._format_currency_value(balance_currency_running[account_id]),
                        'no_format': balance_currency_running[account_id],
                        'class': 'number'
                    })
                elif currency_col_index != -1:
                    # Add new Balance (Currency) column after Currency column
                    currency_column = line['columns'][currency_col_index]
                    column_group_key = currency_column.get('column_group_key')
                    
                    line['columns'].insert(currency_col_index + 1, {
                        'name': self._format_currency_value(balance_currency_running[account_id]),
                        'no_format': balance_currency_running[account_id],
                        'class': 'number',
                        'expression_label': 'balance_currency',
                        'column_group_key': column_group_key
                    })

        return lines

    def _format_currency_value(self, value):
        """Format currency value with proper decimal places and grouping"""
        if value == 0.0:
            return '0.00'
        return '{:,.2f}'.format(value)

    def _report_expand_unfoldable_line_general_ledger(self, line_dict_id, groupby, options, progress, offset, unfold_all_batch_data=None):
        result = super()._report_expand_unfoldable_line_general_ledger(line_dict_id, groupby, options, progress, offset, unfold_all_batch_data)
        
        # Track running balance for expanded lines
        running_balance_currency = 0.0
        
        # Get initial balance from the first line if it's an initial balance line
        if result.get('lines') and len(result['lines']) > 0:
            first_line = result['lines'][0]
            if first_line.get('level') == 2:  # Initial balance line
                for col in first_line.get('columns', []):
                    if col.get('expression_label') == 'amount_currency':
                        running_balance_currency = col.get('no_format', 0.0) or 0.0
                        break
                    elif col.get('expression_label') == 'balance' and running_balance_currency == 0.0:
                        running_balance_currency = col.get('no_format', 0.0) or 0.0
        
        for line in result.get('lines', []):
            if line.get('columns'):
                # Find amount_currency and balance columns
                amount_currency = 0.0
                balance = 0.0
                currency_col_index = -1
                
                for i, col in enumerate(line['columns']):
                    expr_label = col.get('expression_label')
                    if expr_label == 'amount_currency':
                        amount_currency = col.get('no_format', 0.0) or 0.0
                        currency_col_index = i
                    elif expr_label == 'balance':
                        balance = col.get('no_format', 0.0) or 0.0

                # Update running balance for move lines (not initial balance)
                if line.get('level') == 3:  # Move line
                    transaction_amount = amount_currency if amount_currency != 0.0 else balance
                    running_balance_currency += transaction_amount

                # Add or update Balance (Currency) column
                balance_currency_col_index = -1
                for i, col in enumerate(line['columns']):
                    if col.get('expression_label') == 'balance_currency':
                        balance_currency_col_index = i
                        break

                if balance_currency_col_index != -1:
                    # Update existing Balance (Currency) column
                    line['columns'][balance_currency_col_index].update({
                        'name': self._format_currency_value(running_balance_currency),
                        'no_format': running_balance_currency,
                        'class': 'number'
                    })
                elif currency_col_index != -1:
                    # Add new Balance (Currency) column after Currency column
                    currency_column = line['columns'][currency_col_index]
                    column_group_key = currency_column.get('column_group_key')
                    
                    line['columns'].insert(currency_col_index + 1, {
                        'name': self._format_currency_value(running_balance_currency),
                        'no_format': running_balance_currency,
                        'class': 'number',
                        'expression_label': 'balance_currency',
                        'column_group_key': column_group_key
                    })

        return result
