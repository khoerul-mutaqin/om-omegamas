import logging
from odoo import models, fields, api
from datetime import datetime

_logger = logging.getLogger(__name__)


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

