# This file is part of sale_w_tax module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.transaction import Transaction
from trytond.pyson import Eval
from trytond.modules.product import price_digits
from trytond.modules.currency.fields import Monetary
from trytond.modules.product import round_price

_ZERO = Decimal(0)


class SaleLine(metaclass=PoolMeta):
    __name__ = 'sale.line'
    unit_price_w_tax = fields.Function(Monetary('Unit Price with Tax',
        digits=price_digits, currency='currency',
        states={
            'invisible': Eval('type') != 'line',
            }), 'get_unit_price_with_tax')
    amount_w_tax = fields.Function(Monetary('Amount with Tax',
        digits='currency', currency='currency',
        states={
            'invisible': ~Eval('type').in_(['line', 'subtotal']),
            }), 'get_amount_with_tax')

    @fields.depends(methods=['_get_taxes'])
    def get_amount_with_tax(self, name=None):
        if self.type == 'line':
            if self.quantity:
                # Compute amount as we cannot depend on another computed field
                tax_amount = sum((v['amount'] for v in self._get_taxes().values()),
                    Decimal(0))
                amount = self.on_change_with_amount()
                amount += tax_amount
                if self.sale and self.sale.currency:
                    amount = self.sale.currency.round(amount)
                return amount
        elif self.type == 'subtotal':
            amount = Decimal(0)
            for line in self.lines:
                if line.type == 'line':
                    amount += line.get_amount_with_tax()
                if line == self:
                    break
                if line.type == 'subtotal':
                    amount = Decimal(0)
            return amount

    def get_unit_price_with_tax(self, name=None):
        if self.type != 'line':
            return
        if not self.quantity:
            return
        amount = self.get_amount_with_tax()
        return round_price(amount / Decimal(str(self.quantity)))

    @fields.depends('type', 'unit_price', 'quantity', 'taxes', 'sale',
        '_parent_sale.currency', 'currency', 'product', 'amount')
    def on_change_with_unit_price_w_tax(self, name=None):
        if not self.sale:
            self.sale = Transaction().context.get('sale')
        return self.get_unit_price_with_tax()

    @fields.depends('type', 'unit_price', 'quantity', 'taxes', 'sale',
        '_parent_sale.currency', 'currency', 'product', 'amount')
    def on_change_with_amount_w_tax(self, name=None):
        if not self.sale:
            self.sale = Transaction().context.get('sale')
        return self.get_amount_with_tax()
