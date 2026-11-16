from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.mail import send_mail
import uuid
from .models import (
    Shop, Category, Product, ProductInfo, ProductParameter,
    Order, OrderItem, Contact, ConfirmEmailToken
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
        token = str(uuid.uuid4())
        ConfirmEmailToken.objects.create(user=user, token=token)

        send_mail(
            subject='Подтверждение регистрации',
            message=f'Ваш токен для подтверждения: {token}',
            from_email=None,
            recipient_list=[user.email],
            fail_silently=True,
        )

        return user


class ConfirmEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
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


class ProductParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductParameter
        fields = ('id', 'name', 'value')


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
    class Meta:
        model = Contact
        fields = ('id', 'last_name', 'first_name', 'middle_name',
                  'email', 'phone', 'address', 'city', 'street',
                  'house', 'building', 'structure', 'apartment')

    def validate(self, data):
        required_fields = ['last_name', 'first_name', 'email', 'phone', 'address', 'city', 'street', 'house']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f'Поле "{field}" обязательно для заполнения')
        return data


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