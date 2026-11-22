from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Shop, Category, Product, ProductInfo, Parameter, ProductParameter,
    Order, OrderItem, Contact
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'company', 'position', 'type')
        read_only_fields = ('id',)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'company', 'position', 'type')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            company=validated_data.get('company', ''),
            position=validated_data.get('position', ''),
            type=validated_data.get('type', 'buyer'),
            is_active=False
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
    parameters = ProductParameterSerializer(many=True, read_only=True, source='product_parameters')

    class Meta:
        model = ProductInfo
        fields = ('id', 'product', 'shop', 'external_id', 'model',
                  'price', 'price_rrc', 'quantity', 'parameters')


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone')

    def validate(self, data):
        required_fields = ['city', 'street', 'phone']
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
    ordered_items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'dt', 'state', 'contact', 'ordered_items')