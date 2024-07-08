# This file is part sale_w_tax module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import sale
from . import sale_discount
from . import discount_formula

def register():
    Pool.register(
        sale.SaleLine,
        module='sale_w_tax', type_='model')
    Pool.register(
        sale_discount.SaleLine,
        module='sale_w_tax', type_='model', depends=['sale_discount'])
    Pool.register(
        discount_formula.SaleLine,
        module='sale_w_tax', type_='model', depends=['sale_discount', 'discount_formula'])
