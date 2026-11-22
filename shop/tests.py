from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Shop, Category, Product, ProductInfo, Contact, Order, OrderItem

User = get_user_model()


class ShopAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='12345',
            first_name='Тест',
            last_name='Тестов',
            is_active=True
        )
        self.shop = Shop.objects.create(name='Тестовый магазин')
        self.category = Category.objects.create(name='Тестовая категория')
        self.product = Product.objects.create(name='Тестовый товар', category=self.category)
        self.product_info = ProductInfo.objects.create(
            product=self.product,
            shop=self.shop,
            external_id=1,
            model='test-model',
            price=1000,
            price_rrc=1200,
            quantity=10
        )
        self.contact = Contact.objects.create(
            user=self.user,
            city='Москва',
            street='Ленина',
            house='1',
            phone='123456'
        )

    def test_register(self):
        response = self.client.post('/api/register/', {
            'email': 'new@example.com',
            'password': '12345',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'company': 'ООО Тест',
            'position': 'Директор',
            'type': 'buyer'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_login(self):
        response = self.client.post('/api/login/', {
            'email': 'test@example.com',
            'password': '12345'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post('/api/login/', {
            'email': 'test@example.com',
            'password': 'wrong'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_product_list(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_order(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/cart/', {
            'product_info_id': self.product_info.id,
            'quantity': 2
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post('/api/orders/create/', {
            'contact_id': self.contact.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Order.objects.filter(user=self.user, state='new').exists())

    def test_create_order_empty_cart(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/orders/create/', {
            'contact_id': self.contact.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_invalid_contact(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/cart/', {
            'product_info_id': self.product_info.id,
            'quantity': 2
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post('/api/orders/create/', {
            'contact_id': 999
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_quantity(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/cart/', {
            'product_info_id': self.product_info.id,
            'quantity': 'abc'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)