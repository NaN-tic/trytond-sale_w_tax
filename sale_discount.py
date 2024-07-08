from trytond.model import fields
from trytond.pool import PoolMeta


class SaleLine(metaclass=PoolMeta):
    __name__ = 'sale.line'

    @fields.depends(methods=['on_change_with_unit_price_w_tax',
            'on_change_with_amount_w_tax'])
    def on_change_discount_rate(self):
        super().on_change_discount_rate()
        self.unit_price_w_tax = self.on_change_with_unit_price_w_tax()
        self.amount_w_tax = self.on_change_with_amount_w_tax()

    @fields.depends(methods=['on_change_with_unit_price_w_tax',
            'on_change_with_amount_w_tax'])
    def on_change_discount_amount(self):
        super().on_change_discount_amount()
        self.unit_price_w_tax = self.on_change_with_unit_price_w_tax()
        self.amount_w_tax = self.on_change_with_amount_w_tax()

