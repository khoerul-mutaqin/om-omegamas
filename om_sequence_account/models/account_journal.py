# -*- coding: utf-8 -*-

from odoo import models, fields, api
import re

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    sequence_id = fields.Many2one('ir.sequence', 'Reference Sequence',
        copy=False, check_company=True)

    