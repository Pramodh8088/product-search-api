from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Product


class ProductAPITests(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            password="TestPassword@123"
        )

        # Generate a JWT access token
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        # Authenticate all test requests
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        # Create sample products
        self.product1 = Product.objects.create(
            name="Laptop",
            description="Laptop with 16GB RAM and 512GB SSD",
            price=Decimal("55000.00"),
            category="Electronics",
            stock=10
        )

        self.product2 = Product.objects.create(
            name="Wireless Mouse",
            description="Bluetooth wireless mouse",
            price=Decimal("800.00"),
            category="Electronics",
            stock=25
        )

        self.product3 = Product.objects.create(
            name="T-Shirt",
            description="Cotton casual T-shirt",
            price=Decimal("500.00"),
            category="Clothing",
            stock=30
        )

        # Define API URLs
        self.list_url = reverse("product-list-create")

        self.summary_url = reverse("product-summary")

        self.detail_url = reverse(
            "product-detail",
            args=[self.product1.id]
        )

    def test_list_products(self):
        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(response.data["count"], 3)

    def test_create_product(self):
        data = {
            "name": "Keyboard",
            "description": "Wireless keyboard",
            "price": "1200.00",
            "category": "Electronics",
            "stock": 15
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(Product.objects.count(), 4)

    def test_search_product(self):
        response = self.client.get(
            self.list_url,
            {"search": "Laptop"}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(response.data["count"], 1)

        self.assertEqual(
            response.data["results"][0]["name"],
            "Laptop"
        )

    def test_filter_by_category(self):
        response = self.client.get(
            self.list_url,
            {"category": "Electronics"}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(response.data["count"], 2)

    def test_filter_by_price(self):
        response = self.client.get(
            self.list_url,
            {"min_price": "1000"}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(response.data["count"], 1)

        self.assertEqual(
            response.data["results"][0]["name"],
            "Laptop"
        )

    def test_retrieve_product(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["name"],
            "Laptop"
        )

    def test_update_product(self):
        data = {
            "price": "52000.00",
            "stock": 8
        }

        response = self.client.patch(
            self.detail_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.product1.refresh_from_db()

        self.assertEqual(
            self.product1.price,
            Decimal("52000.00")
        )

        self.assertEqual(
            self.product1.stock,
            8
        )

    def test_delete_product(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Product.objects.filter(
                id=self.product1.id
            ).exists()
        )

    def test_summary(self):
        response = self.client.get(self.summary_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["total_products"],
            3
        )

        self.assertEqual(
            response.data["total_stock"],
            65
        )

        self.assertAlmostEqual(
            float(response.data["average_price"]),
            18766.67,
            places=2
        )