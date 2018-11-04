# This file is part of sale_w_tax module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
from trytond.model import fields
from trytond.pool import PoolMeta, Pool
from trytond.transaction import Transaction
from trytond.pyson import Bool, Eval, Not

__all__ = ['SaleLine']
_ZERO = Decimal('0.00')


class SaleLine:
    __metaclass__ = PoolMeta
    __name__ = 'sale.line'
    unit_price_w_tax = fields.Function(fields.Numeric('Unit Price with Tax',
        digits=(16, Eval('_parent_sale', {}).get('currency_digits',
                Eval('currency_digits', 2))),
        states={
            'invisible': Eval('type') != 'line',
            },
        depends=['type', 'currency_digits']), 'get_price_with_tax')
    amount_w_tax = fields.Function(fields.Numeric('Amount with Tax',
        digits=(16, Eval('_parent_sale', {}).get('currency_digits',
                Eval('currency_digits', 2))),
        states={
            'invisible': ~Eval('type').in_(['line', 'subtotal']),
            },
        depends=['type', 'currency_digits']), 'get_price_with_tax')
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
        'on_change_with_currency_digits')
    currency = fields.Many2One('currency.currency', 'Currency',
        states={
            'required': Not(Bool(Eval('sale'))),
            },
        depends=['sale'])

    @staticmethod
    def default_currency_digits():
        Company = Pool().get('company.company')
        if Transaction().context.get('company'):
            company = Company(Transaction().context['company'])
            return company.currency.digits
        return 2

    @staticmethod
    def default_currency():
        Company = Pool().get('company.company')
        if Transaction().context.get('company'):
            company = Company(Transaction().context['company'])
            return company.currency.id

    @fields.depends('currency')
    def on_change_with_currency_digits(self, name=None):
        if self.currency:
            return self.currency.digits
        return 2

    @classmethod
    def get_price_with_tax(cls, lines, names):
        pool = Pool()
        Tax = pool.get('account.tax')
        amount_w_tax = {}
        unit_price_w_tax = {}

        def compute_amount_with_tax(line):
            product_customer_taxes = line.product.template.customer_taxes_used
            party = line.party

            party_taxes = []
            pattern = {}
            for tax in product_customer_taxes:
                if party and party.customer_tax_rule:
                    tax_ids = party.customer_tax_rule.apply(tax, pattern)
                    if tax_ids:
                        party_taxes.extend(tax_ids)
                    continue
                party_taxes.append(tax.id)
            if party and party.customer_tax_rule:
                tax_ids = party.customer_tax_rule.apply(None, pattern)
                if tax_ids:
                    party_taxes.extend(tax_ids)
            line_taxes = Tax.browse(party_taxes) if party_taxes else []
            if not line_taxes:
                line_taxes = product_customer_taxes

            if line_taxes:
                tax_list = Tax.compute(line_taxes,
                    line.unit_price or Decimal('0.0'),
                    line.quantity or 0.0)

                tax_amount = sum([t['amount'] for t in tax_list], Decimal('0.0'))
                amount = sum([t['base'] for t in tax_list], Decimal('0.0'))
            else:
                tax_amount = Decimal('0.0')
                amount = Decimal('0.0')
                if line.unit_price:
                    amount = line.unit_price * Decimal(line.quantity)
            return amount + tax_amount

        for line in lines:
            amount = Decimal('0.0')
            unit_price = Decimal('0.0')
            currency = (line.sale.currency if line.sale else line.currency)

            if line.type == 'line':
                if line.quantity:
                    amount = compute_amount_with_tax(line)
                    unit_price = amount / Decimal(str(line.quantity))

            # Only compute subtotals if the two fields are provided to speed up
            elif line.type == 'subtotal' and len(names) == 2:
                for line2 in line.sale.lines:
                    if line2.type == 'line':
                        amount2 = compute_amount_with_tax(line2)
                        if currency:
                            amount2 = currency.round(amount2)
                        amount += amount2
                    elif line2.type == 'subtotal':
                        if line == line2:
                            break
                        amount = Decimal('0.0')

            if currency:
                amount = currency.round(amount)
            amount_w_tax[line.id] = amount
            unit_price_w_tax[line.id] = unit_price

        result = {
            'amount_w_tax': amount_w_tax,
            'unit_price_w_tax': unit_price_w_tax,
            }
        for key in result.keys():
            if key not in names:
                del result[key]
        return result

    @fields.depends('type', 'unit_price', 'quantity', 'taxes', 'sale',
        '_parent_sale.currency', 'currency', 'product', 'amount')
    def on_change_with_unit_price_w_tax(self, name=None):
        if not self.sale:
            self.sale = Transaction().context.get('sale')
        return SaleLine.get_price_with_tax([self],
            ['unit_price_w_tax'])['unit_price_w_tax'][self.id]

    @fields.depends('type', 'unit_price', 'quantity', 'taxes', 'sale',
        '_parent_sale.currency', 'currency', 'product', 'amount')
    def on_change_with_amount_w_tax(self, name=None):
        if not self.sale:
            self.sale = Transaction().context.get('sale')
        return SaleLine.get_price_with_tax([self],
            ['amount_w_tax'])['amount_w_tax'][self.id]
