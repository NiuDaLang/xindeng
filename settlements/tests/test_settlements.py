# settlements/tests.py

from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from accounts.models import Account
from creators.models import CreatorProfile
from orders.models import Order, OrderProduct
from store.models import Product, Category
from ..models import ArtisanSettlementLine

class SettlementLineFormulaTests(TestCase):
    """
    Tests the net_payable_to_artisan formula. These tests hand-compute
    the expected value and compare it against the property, as requested
    in the session opening remarks.
    """

    @classmethod
    def setUpTestData(cls):
        # Create a basic user/artisan
        cls.artisan_user = Account.objects.create_user(username="artisan1", email="artisan1@test.com", password="pw", receive_newsletter=False)
        cls.artisan_profile = CreatorProfile.objects.create(user=cls.artisan_user, display_name="Test Artisan")

        # Create a basic order structure (details not important for the formula test)
        cls.order = Order.objects.create(order_number="TEST-ORDER-001")
        cls.category = Category.objects.create(category_name="Test Cat", slug="test-cat")
        cls.product = Product.objects.create(product_name="Test Product", category=cls.category, creator=cls.artisan_profile)
        
    def test_property_matches_manual_calculation_for_ddp(self):
        """
        Hand-computes the expected net payable for a single-artisan DDP order
        where the platform fronts all costs.
        """
        line = ArtisanSettlementLine.objects.create(
            order=self.order,
            artisan=self.artisan_profile,
            product_revenue=Decimal('100.00'),
            shipping_charged_to_customer=Decimal('20.00'),
            website_margin_amount=Decimal('20.00'), # Corresponds to '20' in the example
            shipping_paid_by_website=Decimal('25.00'), # Corresponds to '25' in the example
            tax_paid_by_website=Decimal('15.00'), # Corresponds to '15' in the example
            # Artisan-fronted costs are zero
        )
        
        # Hand-computed expected value: 100 + 20 - 20 - 25 - 15 = 60.00
        expected_net_payable = Decimal('60.00')
        
        # Assert the property matches the hand-computed value
        self.assertEqual(line.net_payable_to_artisan, expected_net_payable)

    def test_property_handles_artisan_fronted_costs(self):
        """
        Tests the formula when the artisan fronts some costs, which should be added back.
        """
        line = ArtisanSettlementLine.objects.create(
            order=self.order,
            artisan=self.artisan_profile,
            product_revenue=Decimal('100.00'),
            shipping_charged_to_customer=Decimal('20.00'),
            website_margin_amount=Decimal('15.00'),
            shipping_paid_by_website=Decimal('10.00'),
            tax_paid_by_website=Decimal('5.00'),
            shipping_paid_by_artisan=Decimal('12.00'),
            tax_paid_by_artisan=Decimal('8.00'),
        )
        
        # Hand-computed expected value: 100 + 20 - 15 - 10 - 5 + 12 + 8 = 110.00
        expected_net_payable = Decimal('110.00')
        self.assertEqual(line.net_payable_to_artisan, expected_net_payable)

    def test_property_handles_zeroes_and_negatives(self):
        """
        Tests the formula with negative other_costs and zeroes in various fields.
        """
        line = ArtisanSettlementLine.objects.create(
            order=self.order,
            artisan=self.artisan_profile,
            product_revenue=Decimal('100.00'),
            shipping_charged_to_customer=Decimal('0.00'),
            website_margin_amount=Decimal('0.00'),
            shipping_paid_by_website=Decimal('0.00'),
            tax_paid_by_website=Decimal('10.00'),
            other_costs=Decimal('-20.00'), # Negative adjustment
        )
        # Hand-computed expected value: 100 + 0 - 0 - 0 - 10 + 0 + 0 + (-20) = 70.00
        expected_net_payable = Decimal('70.00')
        self.assertEqual(line.net_payable_to_artisan, expected_net_payable)
