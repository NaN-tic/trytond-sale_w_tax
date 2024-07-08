from decimal import Decimal
import unittest
from proteus import Model
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.modules.account.tests.tools import (create_chart, get_accounts,
    create_fiscalyear)
from trytond.modules.account_invoice.tests.tools import (
    set_fiscalyear_invoice_sequences)
from trytond.tests.tools import activate_modules
from trytond.tests.test_tryton import drop_db


class Test(unittest.TestCase):
    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):
        config = activate_modules(['sale_w_tax', 'sale_discount', 'discount_formula'])

        create_company()
        company = get_company()

        User = Model.get('res.user')
        Group = Model.get('res.group')

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')
        period = fiscalyear.periods[0]

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        receivable = accounts['receivable']
        revenue = accounts['revenue']
        expense = accounts['expense']

        # Create parties
        Party = Model.get('party.party')
        supplier = Party(name='Supplier')
        supplier.save()
        customer = Party(name='Customer')
        customer.save()

        # Create category
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name='Category')
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.save()

        # Create product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')
        Product = Model.get('product.product')
        product = Product()
        template = ProductTemplate()
        template.name = 'product'
        template.account_category = account_category
        template.default_uom = unit
        template.type = 'goods'
        template.salable = True
        template.list_price = Decimal('10')
        product, = template.products
        template.save()
        product, = template.products

        # Sale products testing several on_change calls
        Sale = Model.get('sale.sale')
        SaleLine = Model.get('sale.line')
        sale = Sale()
        sale.party = customer
        sale_line = sale.lines.new()
        sale_line.product = product
        sale_line.quantity = 1.0
        sale_line.base_price = Decimal('10')
        sale_line.discount_formula = '100'
        self.assertEqual(sale_line.unit_price, Decimal('0'))
        self.assertEqual(sale_line.amount_w_tax, Decimal('0'))

        sale_line.discount_formula = '12'
        self.assertEqual(sale_line.unit_price, Decimal('8.80'))
        self.assertEqual(sale_line.unit_price_w_tax, Decimal('8.80'))
        self.assertEqual(sale_line.amount_w_tax, Decimal('8.80'))
