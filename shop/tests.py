from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Shop, Category, Product, ProductInfo, Contact, Order


class ShopAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='12345',
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
            last_name='Иванов',
            first_name='Иван',
            email='test@example.com',
            phone='123456',
            address='ул. Ленина, 1',
            city='Москва',
            street='Ленина',
            house='1'
        )

    def test_register(self):
        response = self.client.post('/api/register/', {
            'email': 'new@example.com',
            'password': '12345',
            'first_name': 'Новый',
            'last_name': 'Пользователь'
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