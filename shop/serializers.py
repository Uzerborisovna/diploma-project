from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import (
    Shop, Category, Product, ProductInfo, Parameter, ProductParameter,
    Order, OrderItem, Contact
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=False
        )

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        send_mail(
            subject='Подтверждение регистрации',
            message=f'Ваш токен для подтверждения: {token}\nВаш uid: {uid}',
            from_email=None,
            recipient_list=[user.email],
            fail_silently=True,
        )

        return user


class ConfirmEmailSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'url', 'state')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ('id', 'name')


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = ParameterSerializer(read_only=True)

    class Meta:
        model = ProductParameter
        fields = ('id', 'parameter', 'value')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'category')


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
    parameters = ProductParameterSerializer(many=True, read_only=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'product', 'shop', 'external_id', 'model',
                  'price', 'price_rrc', 'quantity', 'description', 'parameters')


class ContactSerializer(serializers.ModelSerializer):
    last_name = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    street = serializers.CharField(required=True)
    house = serializers.CharField(required=True)

    class Meta:
        model = Contact
        fields = ('id', 'last_name', 'first_name', 'middle_name',
                  'email', 'phone', 'address', 'city', 'street',
                  'house', 'building', 'structure', 'apartment')


class OrderItemSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'created_at', 'state', 'contact', 'items')