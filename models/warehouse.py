# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from dateutil.relativedelta import relativedelta
from datetime import date,datetime,timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import ValidationError

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    resupply_location_id = fields.Many2one('stock.location',string='Resupply Location',domain="[('usage','=','internal')]")
