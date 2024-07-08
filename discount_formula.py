from trytond.model import fields
from trytond.pool import PoolMeta


class SaleLine(metaclass=PoolMeta):
    __name__ = 'sale.line'

    @fields.depends('discount_formula')
    def on_change_with_unit_price_w_tax(self, name=None):
        return super().on_change_with_unit_price_w_tax(name)

    @fields.depends('discount_formula')
    def on_change_with_amount_w_tax(self, name=None):
        return super().on_change_with_amount_w_tax(name)
