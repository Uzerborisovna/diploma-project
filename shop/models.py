from django.db import models
from django.contrib.auth.models import User


class Shop(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название магазина')
    url = models.URLField(verbose_name='Ссылка на магазин', blank=True, null=True)
    state = models.BooleanField(default=True, verbose_name='Статус приема заказов')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    shops = models.ManyToManyField(Shop, related_name='categories', blank=True, verbose_name='Магазины')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название товара')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products', verbose_name='Магазин')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.shop.name})'


class ProductParameter(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='parameters', verbose_name='Товар')
    name = models.CharField(max_length=100, verbose_name='Характеристика')
    value = models.CharField(max_length=200, verbose_name='Значение')

    class Meta:
        verbose_name = 'Характеристика товара'
        verbose_name_plural = 'Характеристики товаров'

    def __str__(self):
        return f'{self.name}: {self.value}'


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts', verbose_name='Пользователь')
    last_name = models.CharField(max_length=100, default='', verbose_name='Фамилия')
    first_name = models.CharField(max_length=100, default='', verbose_name='Имя')
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Отчество')
    email = models.EmailField(default='default@example.com', verbose_name='Email')
    phone = models.CharField(max_length=20, default='', verbose_name='Телефон')
    address = models.CharField(max_length=200, default='', verbose_name='Адрес')
    city = models.CharField(max_length=100, default='', verbose_name='Город')
    street = models.CharField(max_length=200, default='', verbose_name='Улица')
    house = models.CharField(max_length=50, default='', verbose_name='Дом')
    building = models.CharField(max_length=50, blank=True, null=True, verbose_name='Корпус')
    structure = models.CharField(max_length=50, blank=True, null=True, verbose_name='Строение')
    apartment = models.CharField(max_length=50, blank=True, null=True, verbose_name='Квартира')

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return f'{self.city}, {self.street}, {self.house}'


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'Корзина {self.user.username}'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Корзина')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    class Meta:
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Позиции корзины'

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Пользователь')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, verbose_name='Контакт')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    state = models.CharField(max_length=50, default='new', verbose_name='Статус заказа')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-created_at',)

    def __str__(self):
        return f'Заказ №{self.id} от {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
