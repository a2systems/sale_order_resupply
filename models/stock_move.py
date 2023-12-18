# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from dateutil.relativedelta import relativedelta
from datetime import date,datetime,timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'

    resupply_order_id = fields.Many2one('sale.order',string='Resupply Order')

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    resupply_order_id = fields.Many2one('sale.order',string='Resupply Order')

