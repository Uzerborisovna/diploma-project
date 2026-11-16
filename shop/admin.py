from django.contrib import admin
from .models import (
    Shop, Category, Product, ProductInfo, ProductParameter,
    Contact, Order, OrderItem, ConfirmEmailToken
)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state')
    list_filter = ('state',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'shop', 'price', 'quantity')


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_info', 'name', 'value')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'last_name', 'first_name', 'city')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'state')
    list_filter = ('state',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product_info', 'quantity')


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'token', 'created_at')