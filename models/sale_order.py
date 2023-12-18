# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from dateutil.relativedelta import relativedelta
from datetime import date,datetime,timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    resupply_move_ids = fields.One2many(comodel_name='stock.move',inverse_name='resupply_order_id',string='Resupply Moves')
    resupply_move_line_ids = fields.One2many(comodel_name='stock.move.line',inverse_name='resupply_order_id',string='Resupply Move Lines')

    def action_confirm(self):
        for rec in self:
            rec.resupply_order()
        res = super(SaleOrder, self).action_confirm()
        return res

    def resupply_order(self):
        self.ensure_one()
        if not self.warehouse_id.resupply_location_id:
            raise ValidationError('No esta definido la ubicacion de reabastecimiento')
        for order_line in self.order_line.filtered(lambda l: l.product_id.type == 'product'):
            local_stock_quants = self.env['stock.quant'].search([('location_id','=',self.warehouse_id.lot_stock_id.id),('product_id','=',order_line.product_id.id)])
            local_stock = sum(local_stock_quants.mapped('quantity'))
            if order_line.product_uom_qty > local_stock:
                remote_stock_quants = self.env['stock.quant'].search([('location_id','=',self.warehouse_id.resupply_location_id.id),('product_id','=',order_line.product_id.id)])
                remote_stock = sum(remote_stock_quants.mapped('quantity'))
                if order_line.product_uom_qty > remote_stock:
                    raise ValidationError('No hay stock para el producto %s'%(order_line.product_id.display_name))
                qty = order_line.product_uom_qty
                prod_id = order_line.product_id
                # Source move
                location_adj = self.env['stock.location'].search([
                    ('complete_name','=','Virtual Locations/Inventory adjustment'),
                    ('company_id','=',self.warehouse_id.resupply_location_id.company_id.id),
                    ],limit=1)
                dest_location_adj = self.env['stock.location'].search([
                    ('complete_name','=','Virtual Locations/Inventory adjustment'),
                    ('company_id','=',self.company_id.id),
                    ],limit=1)
                if not location_adj or not dest_location_adj:
                    raise ValidationError('No hay ubicacion Virtual Locations/Inventory adjustment')
                vals_move = {
                            'resupply_order_id': self.id,
                            'product_uom': prod_id.uom_id.id,
                            'product_id': prod_id.id,
                            'name': 'Reabastecimiento inventario %s %s'%(self.name,prod_id.display_name),
                            'company_id': self.warehouse_id.resupply_location_id.company_id.id,
                            'state': 'draft',
                            'is_inventory': True,
                            'location_id': self.warehouse_id.resupply_location_id.id,
                            'location_dest_id': location_adj.id,
                            'product_uom_qty': qty
                            }
                src_move_id = self.env['stock.move'].create(vals_move)
                vals_move_line = {
                            'resupply_order_id': self.id,
                            'move_id': src_move_id.id,
                            'product_uom_id': prod_id.uom_id.id,
                            'product_id': prod_id.id,
                            'state': 'draft',
                            'company_id': self.warehouse_id.resupply_location_id.company_id.id,
                            'location_id': self.warehouse_id.resupply_location_id.id,
                            'location_dest_id': location_adj.id,
                            'qty_done': qty
                            }
                move_line_id = self.env['stock.move.line'].create(vals_move_line)
                vals_move = {
                            'resupply_order_id': self.id,
                            'product_uom': prod_id.uom_id.id,
                            'product_id': prod_id.id,
                            'name': 'Reabastecimiento inventario %s %s'%(self.name,prod_id.display_name),
                            'company_id': self.company_id.id,
                            'state': 'draft',
                            'is_inventory': True,
                            'location_id': dest_location_adj.id,
                            'location_dest_id': self.warehouse_id.lot_stock_id.id,
                            'product_uom_qty': qty
                            }
                dest_move_id = self.env['stock.move'].create(vals_move)
                vals_move_line = {
                            'resupply_order_id': self.id,
                            'move_id': dest_move_id.id,
                            'product_uom_id': prod_id.uom_id.id,
                            'product_id': prod_id.id,
                            'state': 'draft',
                            'company_id': self.company_id.id,
                            'location_id': dest_location_adj.id,
                            'location_dest_id': self.warehouse_id.lot_stock_id.id,
                            'qty_done': qty
                            }
                move_line_id = self.env['stock.move.line'].create(vals_move_line)
                src_move_id._action_done()
                dest_move_id._action_done()
