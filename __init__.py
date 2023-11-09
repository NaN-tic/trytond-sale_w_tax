# This file is part sale_w_tax module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import sale

def register():
    Pool.register(
        sale.SaleLine,
        module='sale_w_tax', type_='model')
    Pool.register(
        sale.SaleLineDiscount,
        module='sale_w_tax', type_='model',
        depends=['sale_discount'])
    Pool.register(
        sale.SaleLineThreeDiscount,
        module='sale_w_tax', type_='model',
        depends=['sale_3_discounts'])
